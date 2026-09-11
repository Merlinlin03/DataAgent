import asyncio
from typing import Optional

from sqlalchemy import text, Select

from app.conf.app_config import DBConfig, app_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker

from app.models.mysql.table_info_mysql import TableInfoMySQL


class MysqlClientManager:
    """
    操作Mysql数据的客户端管理器类
    """
    def __init__(self, config: DBConfig):
        self.config = config
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None

    def _get_url(self):
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"

    def init(self):
        # 创建引擎
        self.engine = create_async_engine(
            self._get_url(),
            pool_size=10, # 连接池的大小，初始创建的常驻连接数，用完后还回来，如果超过了只能创建临时连接，用完后自动断开
            max_overflow=15, # 最大临时连接数，如果超过了，只能等待，在超时时间内有连接还回来了，正常使用，如果没有，报错
            pool_pre_ping=True, # 获取连接时，会自动判断这个连接是否可用，如果不可用，自动创建一个新的返回给你， 防止数据库操作意外失败
        )
        # 创建工厂
        self.session_factory = async_sessionmaker(
            self.engine,
            autobegin=True,  # 默认就是True, 代表自动开启事务， 并不会自动提交事件
            expire_on_commit=False,  # 事务提交后，ORM对象是否过期，为False代表不过期，还可以使用
            autoflush=True,  # 在查询前是否自动将未提交事务的数据更新同步到暂存区 =》是否可以立即查询到  False查不到
        )

    async def close(self):
        await self.engine.dispose()

# 创建操作dw数据库的客户端管理器
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)

# 创建操作meta数据库的客户端管理器
meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)

if __name__ == '__main__':
    # 非ORM的查询
    async def test():
        # 初始化manager
        dw_mysql_client_manager.init()

        # 执行查询
        # 创建一个异步会话对象
        # async with AsyncSession(
        #     dw_mysql_client_manager.engine,
        #     autobegin=True, # 默认就是True, 代表自动开启事务， 并不会自动提交事件
        #     expire_on_commit=True, # 事务提交后，ORM对象是否过期，为False代表不过期，还可以使用
        #     autoflush=False, # 在查询前是否自动将未提交事务的数据更新同步到暂存区 =》是否可以立即查询到  False查不到
        # ) as session:

        # if dw_mysql_client_manager.session_factory is None:
        #     pass
        async with dw_mysql_client_manager.session_factory() as session:
            session: AsyncSession # 声明session类型
            """
            result.all(): 包含n个row对象的数组， row对象可以通过for来遍历包含字段值
            result.mappings().all(): 包含n个rowMapping对象的数组， rowMapping对象可以通过for来遍历出字段名和字段值
            result.scalars().all(): 包含n个第一个字段值的数组
            """
            # 执行sql语句查询
            sql = "select * from dim_country limit 2"
            result = await session.execute(text(sql))
            # 读取数据
            # rows = result.all()
            # print(rows)
            # print(type(rows[0]))
            # for row in rows:
            #     for val in row:
            #         print(val)

            # rows = result.mappings().all()
            # print(rows)
            # print(type(rows[0]))
            # for row in rows:
            #     for key, val in row.items():
            #         print(key, val)

            rows = result.scalars().all()
            print(rows)
            print(type(rows[0]))
            for val in rows:
                print(val)

        # 关闭manager
        await dw_mysql_client_manager.close()

    # 测试orm 添加和查询
    async def test_orm1():
        # 初始化manager
        meta_mysql_client_manager.init()

        async with meta_mysql_client_manager.session_factory() as session:
            session: AsyncSession  # 声明session类型
            table_info1 = TableInfoMySQL(
                id="dim_country2",
                name="dim_country2",
                role="dim",
                description="国家维度测试表"
            )
            session.add(table_info1)
            table_info2 = TableInfoMySQL(
                id="dim_product2",
                name="dim_product2",
                role="dim",
                description="产品表"
            )
            session.add(table_info2)

            # 提交事务
            await session.commit()
            # 在事务提交后访问ORM对象 =》 看expire_on_commit是否为False
            print(table_info1.description)

            # 查询
            table_info = await session.get(TableInfoMySQL, "dim_country2")
            print("查询：", table_info.name, table_info.description)
            result = await session.execute(Select(TableInfoMySQL).limit(2))
            # result = await session.execute(Select(TableInfoMySQL).from_statement(text("select * from table_info limit 2")))
            table_infos: list[TableInfoMySQL] = result.scalars().all()
            print("查询列表：", table_infos)



        # 关闭manager
        await meta_mysql_client_manager.close()

    # 测试orm  更新和删除
    async def test_orm2():
        # 初始化manager
        meta_mysql_client_manager.init()

        async with meta_mysql_client_manager.session_factory() as session:
            session: AsyncSession  # 声明session类型

            table_info = await session.get(TableInfoMySQL, "dim_product")

            # 更新
            # table_info.description = "abcd"

            # 删除
            await session.delete(table_info)

            # 提交事务
            await session.commit()

        # 关闭manager
        await meta_mysql_client_manager.close()

    # 运行测试函数
    # asyncio.run(test())
    asyncio.run(test_orm1())
    # asyncio.run(test_orm2())
