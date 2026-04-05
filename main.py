import os
import datetime
import time

def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')

def obter_turno():
    hora = datetime.datetime.now().hour
    if 6 <= hora < 14: return "Turno_1"
    elif 14 <= hora < 22: return "Turno_2"
    else: return "Turno_3"

def registrar():
    limpar()
    print("--- 🏭 REGISTRO INJEXFLOW ---")
    maquina = input("Nº da Injetora: ")
    q = input("Quantidade BOAS: ")
    r = input("Quantidade REFUGO: ")
    
    if q.isdigit() and r.isdigit():
        q, r = int(q), int(r)
        turno = obter_turno()
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Salva no CSV
        with open("producao.csv", "a") as f:
            f.write(f"{agora},{turno},{maquina},{q},{r}\n")
        
        # Alerta de Qualidade
        if q > 0 and (r / (q + r)) > 0.10:
            print("\n⚠️  ALERTA: REFUGO ACIMA DE 10%!")
            time.sleep(2)
        print("\n✅ SALVO!")
    else:
        print("\n❌ Erro: Use apenas números.")
    time.sleep(1)

while True:
    limpar()
    print("      INJEXFLOW 2.0 🏭")
    print("="*25)
    print("1 - Registrar Produção")
    print("2 - Ver Resumo")
    print("3 - Sair")
    op = input("\nEscolha: ")
    if op == "1": registrar()
    elif op == "2":
        limpar()
        print("--- 📊 DADOS GRAVADOS ---")
        try:
            with open("producao.csv", "r") as f: print(f.read())
        except: print("Sem dados.")
        input("\n[ENTER para voltar]")
    elif op == "3": break
