from secrets import token_bytes

from pydantic import BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    DB_SCHEMA: str = "postgresql+psycopg"

    SECRET_KEY: str = Field(default_factory=token_bytes(16).hex)
    TOKEN_LIFETIME: float = 60 * 60 * 24

    @property
    def POSTGRES_DSN(self) -> str:
        return PostgresDsn.build(
            scheme=self.DB_SCHEMA,
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            path=f"/{self.DB_NAME}",
        )


settings = Settings()
