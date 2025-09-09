from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    애플리케이션 환경 변수 설정을 위한 클래스입니다.
    .env 파일을 읽어와 변수를 설정합니다.
    """

    # 프로젝트 기본 설정
    PROJECT_NAME: str = "FastAPI Mini Project"
    API_V1_STR: str = "/api/v1"

    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # PostgreSQL DB 설정
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    DATABASE_URL: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"  # .env 파일 사용

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DATABASE_URL = (
            f"postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
