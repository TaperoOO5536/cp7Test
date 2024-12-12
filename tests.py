import pytest, asyncio, aiohttp, aiosqlite

#  тест, который проверяет, что функция, которая возвращает promise(future), разрешается с ожидаемым значением
async def func1():
  await asyncio.sleep(0.1)
  return "expected_value"

@pytest.mark.asyncio
async def test1(event_loop):
  result = await func1()
  assert result == "expected_value"

# тест, который проверяет, что функция, которая возвращает промис, отклоняется с ожидаемым исключением
async def func2():
  await asyncio.sleep(0.1)
  raise ValueError("expected_exception")

@pytest.mark.asyncio
async def test2(event_loop):
  with pytest.raises(ValueError) as exc_info:
      await func2()
  assert str(exc_info.value) == "expected_exception"    

# тест, который проверяет, что функция, которая выполняет HTTP-запрос к внешнему API, возвращает корректный ответ
async def fetch_data(url):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      return await response.text()

@pytest.mark.asyncio
async def test3(event_loop):
  url = "https://petstore.swagger.io/v2/swagger.json"
  response = await fetch_data(url)
  assert "swagger" in response
# тест, который проверяет, что функция, которая работает с базой данных, корректно добавляет новую запись
async def insert(db_path):
  async with aiosqlite.connect(db_path) as db:
    await db.execute("INSERT INTO test_table (name) VALUES (?)", ("test_name",))
    await db.commit()

@pytest.mark.asyncio
async def test4(event_loop, tmp_path):
  db_path = tmp_path / "test.db"
  async with aiosqlite.connect(db_path) as db:
    await db.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
    await db.commit()

  await insert(db_path)

  async with aiosqlite.connect(db_path) as db:
    async with db.execute("SELECT name FROM test_table") as cursor:
       result = await cursor.fetchone()
       assert result[0] == "test_name"
# тест, который проверяет, что функция, которая запускает другую асинхронную функцию в отдельном потоке, корректно возвращает результат
async def func3():
  await asyncio.sleep(1)
  return "expected_result"

async def func4():
  result = await asyncio.to_thread(asyncio.run, func3())
  return result

@pytest.mark.asyncio
async def test5():
  result = await func4()
  assert result == "expected_result"