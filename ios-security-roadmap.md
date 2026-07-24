# iOS Security Research Roadmap (do zero ao Bug Bounty)

## Fase 1: Fundamentos (1-2 meses)

### Programação
- [ ] **Python** (essencial para ferramentas como Frida)
  - Curso grátis: https://www.youtube.com/playlist?list=PLvE-ZAFRgX8hnECDn1P8x8U7GkD9iZ4Dq
  - Foco: ctypes, sockets, struct packing/unpacking
- [ ] **C** (para entender exploits de baixo nível)
  - Livro: "The C Programming Language" - K&R
- [ ] **Objective-C** runtime (iOS usa isso)
  - Entender mensagens, Method Swizzling, ISA pointers

### Arquitetura
- [ ] **ARM64 assembly** (todo iPhone moderno é ARM64)
  - Ler: "ARM Architecture Reference Manual ARMv8"
  - Praticar: https://godbolt.org (compilar C pra ARM e analisar)
- [ ] **Memória virtual**, páginas, permissões (RWX)

### Sistemas Operacionais
- [ ] **XNU kernel** (kernel do iOS/macOS)
  - Mach messages, task/thread, IPC
- [ ] **Unix basics**: processos, syscalls, signals

---

## Fase 2: Ferramentas Essenciais (2-3 meses)

### Setup Windows + WSL (pra começar)
```powershell
# Instalar WSL2 (Ubuntu) - ESSENCIAL para ferramentas Linux
wsl --install -d Ubuntu
```

### Dentro do WSL/Ubuntu (ou dual boot Linux):
```bash
# Python 3 + pip
sudo apt install python3 python3-pip

# Ferramentas de análise estática
sudo apt install radare2  # disassembler poderoso
pip install capstone      # disassembly framework

# Frida - dynamic instrumentation (ESSENCIAL)
pip install frida-tools

# Theos - toolchain para tweaks/exploits iOS
git clone https://github.com/theos/theos.git ~/theos

# Ghidra - SRE suite (USAR NO WINDOWS)
# Baixar de: https://ghidra-sre.org/

# checkra1n/palera1n - jailbreak pra dispositivos compatíveis
```

### Ferramentas Windows (interface gráfica):
- **Ghidra** (análise estática)
- **IDA Pro Free** (disassembler)
- **Hopper** (outro disassembler)
- **iMazing / libimobiledevice** (gerenciar dispositivo)

---

## Fase 3: Setup de Teste

### Hardware necessário
- **iPhone/iPad com jailbreak** (usado, barato)
  - iPhone 7/8 (A10/A11) - palera1n jailbreak
  - iPhone XR/XS (A12) - checkra1n (se compatível)
  - iPad 6th gen (barato pra começar)
- **Mac minimal** (opcional mas facilita) - Hackintosh ou Mac Mini 2014 ~R$1500

### Jailbreak + Theos
```bash
# Após jailbreak com palera1n:
git clone https://github.com/theos/theos.git
cd theos && ./bootstrap.sh

# Criar primeiro tweak
nic.pl
# Escolher: "tweak" -> "bundle filter" -> "com.apple.springboard"
```

---

## Fase 4: Tópicos Específicos pra Bug Bounty

### Attack Surface do iOS 26.1
1. **Kernel** (XNU)
   - Race conditions em syscalls
   - Use-after-free em IPC (Mach messages)
   - Integer overflows em IOConnectCallMethod
   
2. **WebKit** (Safari)
   - JavaScriptCore JIT bugs
   - Use-after-free em DOM objects
   - Type confusions

3. **Networking stack**
   - Wi-Fi driver bugs (Broadcom)
   - Bluetooth (lower stack)
   - Baseband (qualcomm/intel)

4. **Sandbox escapes**
   - File system quirks
   - XPC service bugs

### Recursos pra se inspirar
- **Google Project Zero blog** - writeups reais de iOS bugs
- **Apple Security Research dev blog**
- **Saar Amar's iOS kernel série** (YouTube)
- **Azeria's ARM64 exploitation series**
- **r/jailbreak** e **r/netsec**
- **iPhone Wiki** (https://theiphonewiki.com) - hardware details

---

## Fase 5: Como Reportar pra Apple

1. Criar conta em: https://security.apple.com/bounty/
2. Reportar precisa ter:
   - **PoC funcional** (código que reproduz)
   - **Análise da root cause**
   - **Impacto demonstrado**
3. Prazos: Apple responde em ~2-4 semanas
4. Pagamentos: de $5k a $500k dependendo da severidade

---

## Timeline Realista

| Período | Objetivo |
|---------|----------|
| Mês 1-2 | Fundamentos + Python + C |
| Mês 3-4 | ARM64 + Frida + Ghidra |
| Mês 5-6 | Jailbreak + Theos + primeiros tweaks |
| Mês 7-9 | Estudar writeups de CVEs |
| Mês 10-12 | Primeiras tentativas de bug bounty |

---

## Canais pra aprender (grátis)

1. **"iOS Application Security" - via YouTube** (canal: "NowSecure")
2. **"ARM64 Exploitation" - Azeria** (https://azeria-labs.com)
3. **"Modern Binary Exploitation" - RPISEC** (curso completo PDF)
4. **"Pwn2Own" writeups** (ver como os pros fazem)
5. **Discord: "The Apple Researcher"** (comunidade ativa)

---

> **Dica importante:** Não suba exploits que encontrar em fóruns. Se for reportar algo que outra pessoa descobriu, a Apple rejeita e você pode tomar block permanente do programa. Seja original.
