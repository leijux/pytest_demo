import aiomysql
from typing import List, Dict, Any, Optional, AsyncGenerator


class MySQLClient:
    """异步MySQL数据库操作工具类"""

    def __init__(
            self,
            host: str,
            port: int,
            database: str,
            user: str,
            password: str,
            **kwargs
    ):
        """
        初始化数据库连接参数
        :param host: 数据库地址
        :param port: 端口号
        :param database: 数据库名称
        :param user: 用户名
        :param password: 密码
        :param kwargs: 其他连接参数
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn_args = kwargs
        self.pool: Optional[aiomysql.Pool] = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        """创建连接池（推荐使用连接池）"""
        try:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                db=self.database,
                user=self.user,
                password=self.password,
                autocommit=False,
                **self.conn_args
            )
        except aiomysql.OperationalError as e:
            raise ConnectionError(f"数据库连接失败: {str(e)}")

    async def close(self):
        """关闭所有连接"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def execute_query(
            self,
            query: str,
            params: Optional[dict] = None
    ) -> List[Dict[str, Any]]:
        """
        执行查询语句（异步）
        :param query: SQL查询语句
        :param params: 查询参数（字典格式）
        :return: 查询结果列表（字典形式）
        """
        if not self.pool:
            raise RuntimeError("数据库未连接")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute(query, params)
                    return await cursor.fetchall()
                except aiomysql.Error as e:
                    await conn.rollback()
                    raise RuntimeError(f"查询执行失败: {str(e)}")

    async def execute_update(
            self,
            query: str,
            params: Optional[dict] = None
    ) -> int:
        """
        执行更新操作（异步）
        :param query: SQL语句
        :param params: 参数（字典格式）
        :return: 受影响的行数
        """
        if not self.pool:
            raise RuntimeError("数据库未连接")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(query, params)
                    await conn.commit()
                    return cursor.rowcount
                except aiomysql.Error as e:
                    await conn.rollback()
                    raise RuntimeError(f"更新操作失败: {str(e)}")

    async def batch_insert(
            self,
            table: str,
            data: List[Dict[str, Any]]
    ) -> int:
        """
        批量插入数据（异步）
        :param table: 表名
        :param data: 数据字典列表
        :return: 插入的行数
        """
        if not data:
            return 0

        columns = list(data[0].keys())
        values = [tuple(item.values()) for item in data]
        placeholders = ','.join(['%s'] * len(columns))

        query = f"INSERT INTO `{table}` ({', '.join(columns)}) VALUES ({placeholders})"

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.executemany(query, values)
                    await conn.commit()
                    return cursor.rowcount
                except aiomysql.Error as e:
                    await conn.rollback()
                    raise RuntimeError(f"批量插入失败: {str(e)}")

    async def table_exists(self, table_name: str) -> bool:
        """检查表是否存在（异步）"""
        query = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = %(table_name)s
        """
        result = await self.execute_query(query, {"table_name": table_name})
        return result[0]['count'] > 0

    # 添加事务管理
    async def transaction(self, queries: List[tuple]):
        """执行事务操作"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await conn.begin()
                    for query, params in queries:
                        await cursor.execute(query, params)
                    await conn.commit()
                except aiomysql.Error:
                    await conn.rollback()
                    raise

    # 添加流式查询
    async def stream_query(self, query: str, params: dict = None):
        """流式读取大量数据"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.SSCursor) as cursor:
                await cursor.execute(query, params)
                while True:
                    rows = await cursor.fetchmany(1000)
                    if not rows:
                        break
                    for row in rows:
                        yield row
# pytest测试示例 ##################################################

# conftest.py配置
# @pytest.fixture
# async def mysql_client() -> AsyncGenerator[MySQLClient, None]:
#     client = MySQLClient(
#         host="localhost",
#         port=3306,
#         database="testdb",
#         user="root",
#         password="your_password",
#         pool_recycle=3600,
#         pool_size=5
#     )
#     await client.connect()
#     yield client
#     await client.close()
#
#
# # 测试用例（需要pytest-asyncio插件）
# @pytest.mark.asyncio
# async def test_mysql_operations(mysql_client):
#     # 测试表存在检查
#     assert await mysql_client.table_exists("users") is True
#
#     # 测试数据插入
#     test_data = {"username": "test_user", "email": "test@example.com"}
#     insert_sql = """
#         INSERT INTO users (username, email)
#         VALUES (%(username)s, %(email)s)
#     """
#     affected = await mysql_client.execute_update(insert_sql, test_data)
#     assert affected == 1
#
#     # 验证数据
#     select_sql = "SELECT * FROM users WHERE username = %(username)s"
#     results = await mysql_client.execute_query(select_sql, {"username": "test_user"})
#     assert len(results) == 1
#     assert results[0]["email"] == "test@example.com"
#
#     # 清理测试数据
#     delete_sql = "DELETE FROM users WHERE username = %(username)s"
#     await mysql_client.execute_update(delete_sql, {"username": "test_user"})
