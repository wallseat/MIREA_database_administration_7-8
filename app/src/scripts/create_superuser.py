from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import engine
from src.core.role import Entity, Permission
from src.models import Role, User, UserRole


async def main() -> None:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        username = input("Введите username: ")
        email = input("Введите email: ")

        user = await session.scalar(
            select(User).where(or_(User.username == username, User.email == email)),
        )
        if user:
            print("Пользователь с таким логином или почтой уже существует!")
            exit(-1)

        password = input("Введите пароль: ")
        while password != input("Повторите пароль: "):
            print("Пароли не совпадают")
            password = input("Введите пароль: ")

        user = User(username=username, email=email, password=password)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        admin_role = await session.scalar(select(Role).where(Role.name == "Admin"))
        if not admin_role:
            admin_role = Role("Admin", {Entity.ANY.value: [Permission.ALL.value]})
            session.add(admin_role)
            await session.commit()
            await session.refresh(admin_role)

        session.add(UserRole(user_id=user.id_, role_id=admin_role.id_))
        await session.commit()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
