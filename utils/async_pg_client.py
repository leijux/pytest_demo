import psycopg
from psycopg import sql
from psycopg.abc import Query
from psycopg.rows import dict_row
from typing import List, Dict, Any, Optional, AsyncGenerator
from typing import LiteralString


class PostgreSQLClient:
    """异步PostgreSQL操作工具类（psycopg3实现）"""

    def __init__(
            self,
            host: str,
            port: int,
            database: str,
            user: str,
            password: str
    ):
        """
        初始化数据库连接参数
        :param host: 数据库地址
        :param port: 端口号
        :param database: 数据库名称
        :param user: 用户名
        :param password: 密码
        """
        self.dsn = f"dbname={database} user={user} password={password} host={host} port={port}"
        self.conn: Optional[psycopg.AsyncConnection] = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        """建立异步数据库连接"""
        try:
            self.conn = await psycopg.AsyncConnection.connect(
                self.dsn,
                row_factory=dict_row  # 返回字典格式结果
            )
        except psycopg.OperationalError as e:
            raise ConnectionError(f"数据库连接失败: {str(e)}")

    async def close(self):
        """关闭数据库连接"""
        if self.conn:
            await self.conn.close()

    async def execute_query(
            self,
            query: Query,
            params: Optional[dict] = None
    ) -> List[Dict[str, Any]]:
        """
        执行查询语句
        :param query: SQL查询语句
        :param params: 查询参数（字典格式）
        :return: 查询结果列表（字典形式）
        """
        if not self.conn:
            raise RuntimeError("数据库未连接")

        async with self.conn.cursor() as cursor:
            try:
                await cursor.execute(query, params)
                return await cursor.fetchall()
            except psycopg.Error as e:
                await self.conn.rollback()
                raise RuntimeError(f"查询执行失败: {str(e)}")

    async def execute_update(
            self,
            query: Query,
            params: Optional[dict] = None
    ) -> int:
        """
        执行更新操作
        :param query: SQL语句
        :param params: 参数（字典格式）
        :return: 受影响的行数
        """
        if not self.conn:
            raise RuntimeError("数据库未连接")

        async with self.conn.cursor() as cursor:
            try:
                await cursor.execute(query, params)
                await self.conn.commit()
                return cursor.rowcount
            except psycopg.Error as e:
                await self.conn.rollback()
                raise RuntimeError(f"更新操作失败: {str(e)}")

    async def batch_insert(
            self,
            table: str,
            data: List[Dict[str, Any]]
    ) -> int:
        """
        批量插入数据
        :param table: 表名
        :param data: 数据字典列表
        :return: 插入的行数
        """
        if not data:
            return 0

        columns = list(data[0].keys())
        values = [tuple(item.values()) for item in data]

        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join([sql.Placeholder()] * len(columns))
        )

        if not self.conn:
            raise RuntimeError("数据库未连接")

        try:
            async with self.conn.cursor() as cursor:
                await cursor.executemany(query, values)
                await self.conn.commit()
                return cursor.rowcount
        except psycopg.Error as e:
            await self.conn.rollback()
            raise RuntimeError(f"批量插入失败: {str(e)}")

    async def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        query: LiteralString = """
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename = %(table_name)s
            )
        """

        result = await self.execute_query(query, {"table_name": table_name})
        return result[0]['exists']

# pytest异步测试示例 ##############################################

# # conftest.py配置
# @pytest.fixture
# async def async_db() -> AsyncGenerator[AsyncPostgreSQL, None]:
#     db = AsyncPostgreSQL(
#         host="localhost",
#         port=5432,
#         database="testdb",
#         user="postgres",
#         password="your_password"
#     )
#     await db.connect()
#     yield db
#     await db.close()
#
#
# # 测试用例示例（需要pytest-asyncio插件）
# @pytest.mark.asyncio
# async def test_async_query(async_db):
#     # 测试表存在检查
#     assert await async_db.table_exists("users") is True
#
#     # 测试插入数据
#     test_data = {"username": "test_user", "email": "test@example.com"}
#     insert_sql = """
#         INSERT INTO users (username, email)
#         VALUES (%(username)s, %(email)s)
#     """
#     affected = await async_db.execute_update(insert_sql, test_data)
#     assert affected == 1
#
#     # 验证插入结果
#     query_sql = "SELECT * FROM users WHERE username = %(username)s"
#     results = await async_db.execute_query(query_sql, {"username": "test_user"})
#     assert len(results) == 1
#     assert results[0]["email"] == "test@example.com"
#
#     # 清理测试数据
#     delete_sql = "DELETE FROM users WHERE username = %(username)s"
#     await async_db.execute_update(delete_sql, {"username": "test_user"})
