from app.database.user_repository import create_user, validate_login

print("Criando usuário...")
ok = create_user("admin", "1234")

print("Criado?", ok)

print("Testando login:")
print(validate_login("admin", "1234"))
print(validate_login("admin", "senha_errada"))
