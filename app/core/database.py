"""데이터베이스 모듈 - SQLAlchemy를 사용한 사용자 정의 예제 관리

이 모듈은 ExampleDatabase 클래스를 제공하여 사용자 정의 예제에 대한 모든 데이터베이스 작업을 처리합니다.
데이터베이스는 SQLAlchemy ORM과 SQLite를 사용하며, 예제의 이름, 설명, RFC 버전 및 원시 메시지 내용과 같은 메타데이터를 저장합니다.
"""
from datetime import datetime
from sqlite3 import DataError, IntegrityError, OperationalError, ProgrammingError
from typing import List, Optional
from sqlalchemy import create_engine, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session, Mapped, mapped_column
from app.models.example import CustomExample


Base = declarative_base()


class CustomExampleModel(Base):
    """커스텀 예시 syslog 모델
    """
    __tablename__ = "custom_examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    rfc_version: Mapped[str] = mapped_column(String, nullable=False)
    raw_message: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ExampleDatabase:
    """커스텀 예제 데이터베이스 클래스  

    이 클래스는 커스텀 예제를 저장, 조회, 수정, 삭제할 수 있는 데이터베이스 인터페이스를 제공합니다.
    SQLAlchemy ORM 기반으로 구현되어 있으며, RFC 버전별로 예제를 관리할 수 있습니다.
    """

    def __init__(self, db_path: str = "examples.db") -> None:
        """초기화  
        db 파일(sqllite) 경로를 설정하고 SQLAlchemy 엔진과 세션을 초기화합니다.

        Args:
            db_path (str, optional): db 파일 경로. Defaults to "examples.db".
        """
        self.db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(self.db_url, echo=False)
        self.session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)
        self.init_db()

    def init_db(self) -> None:
        """db 테이블 생성  
        SQLAlchemy를 사용하여 db 테이블을 생성합니다.  
        """
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """데이터베이스 세션 반환 함수  

        이 함수는 데이터베이스와의 연결 세션을 생성하여 반환합니다. 
        세션은 데이터베이스 작업을 수행하는 데 필요한 컨텍스트를 제공하며,
        트랜잭션 관리 및 쿼리 실행에 사용됩니다.
        
        Returns:
            Session: 생성된 데이터베이스 세션 객체
        """
        return self.session_local()

    def _model_to_pydantic(self, model: CustomExampleModel) -> CustomExample:
        """모델 객체를 Pydantic 모델로 변환  
        
        데이터베이스 모델에서 Pydantic 모델로 필드를 매핑하여 반환한다. 
        모든 필드가 일치하도록 정확하게 매핑되며, 생성일자와 수정일자는 
        데이터베이스의 원본 값을 그대로 유지한다.
        """
        return CustomExample(
            id=model.id,
            name=model.name,
            description=model.description,
            rfc_version=model.rfc_version,
            raw_message=model.raw_message,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def create_example(self,
                       name: str,
                       description: Optional[str],
                       rfc_version: str,
                       raw_message: str) -> CustomExample:
        """커스텀 예제 저장  

        데이터베이스에 신규 예제를 저장합니다.

        Args:
            name (str): 예제 이름
            description (Optional[str]): 예제 설명
            rfc_version (str): RFC 버전 (3164 또는 5424)
            raw_message (str): raw 메시지 내용

        Returns:
            CustomExample: 생성된 예제 객체
        """
        now = datetime.now()

        with self.get_session() as session:
            db_example = CustomExampleModel(
                name=name,
                description=description,
                rfc_version=rfc_version,
                raw_message=raw_message,
                created_at=now,
                updated_at=now
            )

            try:
                session.add(db_example)
                session.commit()
                session.refresh(db_example)

                return self._model_to_pydantic(db_example)
            except IntegrityError as e:
                session.rollback()
                raise ValueError(f"중복된 데이터입니다: {str(e)}") from e
            except DataError as e:
                session.rollback()
                raise ValueError(f"데이터 형식 오류: {str(e)}") from e
            except OperationalError as e:
                session.rollback()
                raise ConnectionError(f"데이터베이스 연결 오류: {str(e)}") from e
            except ProgrammingError as e:
                session.rollback()
                raise ValueError(f"SQL 문법 오류: {str(e)}") from e
            except Exception as e:
                session.rollback()
                raise RuntimeError(f"예상치 못한 오류 발생: {str(e)}") from e

    def get_examples(self, rfc_version: Optional[str] = None) -> List[CustomExample]:
        """예제 리턴  

        데이터베이스에서 예제 정보를 읽어와 리턴한다.
        rfc_version 값을 전달인자로 받아 필터링한다.

        Args:
            rfc_version (Optional[str], optional): rfc버전. Defaults to None.

        Returns:
            List[CustomExample]: 예제 리스트
        """
        with self.get_session() as session:
            query = session.query(CustomExampleModel)

            if rfc_version:
                query = query.filter(CustomExampleModel.rfc_version == rfc_version)

            db_examples = query.order_by(CustomExampleModel.created_at.desc()).all()
            return [self._model_to_pydantic(example) for example in db_examples]

    def get_example(self, example_id: int) -> Optional[CustomExample]:
        """ID로 예제 조회  

        데이터베이스에서 ID로 조회한다.

        Args:
            example_id (int): 조회할 예제의 ID

        Returns:
            Optional[CustomExample]: 예제 데이터 또는 None
        """
        with self.get_session() as session:
            db_example = session.query(CustomExampleModel).filter(
                CustomExampleModel.id == example_id
            ).first()

            if db_example:
                return self._model_to_pydantic(db_example)
            return None

    def update_example(self, example_id: int, name: Optional[str] = None,
                       description: Optional[str] = None, rfc_version: Optional[str] = None,
                       raw_message: Optional[str] = None) -> Optional[CustomExample]:
        """지정된 ID의 예제 수정  

        주어진 예제 ID에 해당하는 데이터를 찾아서, 전달된 파라미터들을 기반으로 필드를 업데이트합니다.
        업데이트 가능한 필드는 이름(name), 설명(description), RFC 버전(rfc_version), 원시 메시지(raw_message)입니다.
        모든 업데이트 후에는 updated_at 타임스탬프가 자동으로 갱신됩니다.
        만약 해당 ID의 예제가 존재하지 않으면 None을 반환합니다.

        Args:
            example_id (int): 업데이트할 예제의 고유 ID
            name (Optional[str], optional): 새로운 이름. None이면 변경되지 않습니다.
            description (Optional[str], optional): 새로운 설명. None이면 변경되지 않습니다.
            rfc_version (Optional[str], optional): 새로운 RFC 버전. None이면 변경되지 않습니다.
            raw_message (Optional[str], optional): 새로운 원시 메시지. None이면 변경되지 않습니다.

        Returns:
            Optional[CustomExample]: 업데이트된 예제 모델 인스턴스 또는 존재하지 않으면 None
        """
        with self.get_session() as session:
            db_example = session.query(CustomExampleModel).filter(
                CustomExampleModel.id == example_id
            ).first()

            if not db_example:
                return None

            if name is not None:
                db_example.name = name
            if description is not None:
                db_example.description = description
            if rfc_version is not None:
                db_example.rfc_version = rfc_version
            if raw_message is not None:
                db_example.raw_message = raw_message

            db_example.updated_at = datetime.now()

            session.commit()
            session.refresh(db_example)

            return self._model_to_pydantic(db_example)

    def delete_example(self, example_id: int) -> bool:
        """예제를 데이터베이스에서 삭제  

        주어진 ID에 해당하는 예제를 데이터베이스에서 찾아서 삭제합니다. 
        예제가 존재하지 않을 경우 False를 반환하며, 성공적으로 삭제된 경우 True를 반환합니다.
        데이터베이스 세션을 자동으로 관리하고, 삭제 작업 후 커밋합니다.

        Args:
            example_id (int): 삭제할 예제의 고유 ID

        Returns:
            bool: 예제 삭제 성공 여부. 존재하지 않는 경우 False를 반환합니다.
        """
        with self.get_session() as session:
            db_example = session.query(CustomExampleModel).filter(
                CustomExampleModel.id == example_id
            ).first()

            if db_example:
                session.delete(db_example)
                session.commit()
                return True
            return False


# Global database instance
example_db = ExampleDatabase()
