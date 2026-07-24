# 🔍 Dark Pro Premium (flashcel) — Análise Forense Completa

> **Status:** Servidor ativo (`isalldone.com.br`) · v6.5.8 (instalada) · v6.6.0 (última no servidor)  
> **Tool real:** `flashcel` / `FlashcelBypass` — **não se chama "Dark Pro Premium"**  
> **Desenvolvedor:** `DM1LN3` · **Bundle ID:** `com.dm1ln3.tool.DarkProPremium`

---

## 📋 Resumo das Descobertas

A engenharia reversa completa do executável "Dark Pro Premium.exe" (228 MB) revelou que se trata de um **app Tauri 1.8.3 (Rust + WebView2)** construído em cima do jailbreak open-source **palera1n** (checkm8). O nome real do projeto é **flashcel**. Abaixo, as evidências técnicas de falsas alegações de marketing e a arquitetura real do exploit.

---

## 🚨 Evidências de Falso Marketing

| Alegação | Realidade |
|----------|-----------|
| "Suporte A12 / A13" | checkm8 funciona **apenas até A11** (iPhone X, 2017) |
| "iOS 17, 18, 19, 20, 21, 22, 23, 24, 25, 26" | **NENHUMA** ocorrência nos 177 MB de .rdata. O exploit real (palera1n) suporta no máximo **iOS 12.0 – 16.5** |
| "Remove iCloud 100%" | Bypass **temporário** via checkm8. Uma reinicialização desfaz |
| "Ferramenta premium/paga" | Código **open-source** (palera1n + checkra1n) empacotado com interface Tauri |

As strings "iOS 17" a "iOS 26" foram exaustivamente buscadas com `rz-find` em todo o .rdata de 177 MB — **zero resultados**.

---

## 🏗️ Arquitetura do App

```
┌─────────────────────────────────────────────────┐
│              Tauri 1.8.3 (Rust)                  │
│  ┌───────────────────────────────────────────┐   │
│  │         WebView2 (HTML/JS/CSS)            │   │
│  │         Interface gráfica do usuário       │   │
│  └───────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────┐   │
│  │         Rust Backend (flashceld)           │   │
│  │  • flashcel_app_state                     │   │
│  │  • flashcel_auth.rs (autenticação)        │   │
│  │  • flashceld/commands.rs                  │   │
│  │  • flashceld/modules/device_commands.rs   │   │
│  │  • socket/handlers/prepare_device.rs      │   │
│  │  • src-tauri/download/utils.rs            │   │
│  └───────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────┐   │
│  │        checkm8 ARM64 Payload (100KB)       │   │
│  │        Extraído do .rdata @ ~14.8 MB       │   │
│  │        Código ARM64 válido com funções     │   │
│  └───────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────┐   │
│  │        Drivers USB (Windows)               │   │
│  │  • PongoOS • DFU PWNDFU • Recovery        │   │
│  │  • libusb0.dll • libusbK.dll              │   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Dependências Rust Identificadas
```
tauri 1.8.3         reqwest 0.11.27      hyper 0.14.32
tokio 1.52.1        serde 1.0.228        mime 0.3.17
state 0.5.3         minisign-verify 0.2.5
```
Compilação: `x86_64-pc-windows-gnu` (MinGW)

---

## 🌐 Servidor & Conexão de Rede

### Servidor ativo: `isalldone.com.br` (Brasil) 🇧🇷

**Endpoint de versão (Tauri updater):**
```
GET https://isalldone.com.br/app/versions/DarkProPremium
```
**Resposta (24/07/2026):**
```json
{
  "version": "6.6.0",
  "notes": "New Update",
  "platforms": {
    "windows-x86_64": {
      "url": "https://isalldone.com.br/app/downloads/Dark_Pro_Premium.msi.zip",
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9tIHRhdXJpIHNlY3JldCBrZXkK..."
    }
  }
}
```

### Domínios Autorizados (Tauri Allowlist)
```
https://isalldone.com/*
https://*.isalldone.com/*
https://isalldone.com.br/*
https://*.isalldone.com.br/*
https://*.apple.com/*
https://localhost:3000/../dist
```

### API Pública: `api.ipsw.me`
O app consulta `api.ipsw.me/v4/device/%s` para verificar quais versões do iOS ainda estão assinadas pela Apple.

### Strings de Servidor Encontradas
```
server envelope
Invalid JSON structure
Invalid base64 input
__FLASHCEL_REPLACE_ED25
AMAuthInstallSetFDRRequestEntry
flashcel-wireless-state
flashcel-wireless-toggle
```

---

## ⚙️ Cadeia do Exploit (checkm8 + palera1n)

```
1. Interface Tauri/WebView2
       ↓
2. Instala drivers USB (SetupAPI)
       ↓
3. Conecta iDevice DFU (libusb)
       ↓
4. Envia checkm8 ARM64 (100KB)
       ↓
5. PongoOS carrega no dispositivo
       ↓
6. Kernel patches + dyld + fakefs
       ↓
7. activation_bypass + restore mods
       ↓
8. Server check (isalldone.com.br)
```

### Strings-chave do Exploit
| String | Função |
|--------|--------|
| `fakefs` | Fake root filesystem |
| `pongo_usb_send_ramdisk` | Envio de ramdisk via USB |
| `pwndfu` | Driver DFU pwnado |
| `platform_check` | Bypass de verificação de plataforma |
| `xnu_untag_va` | Untag de endereços virtuais do XNU |
| `and_patch_dyld` | Patch do dyld |
| `mount_rdisk` | Montagem de disco raw |
| `construct_patch` | Construção de patches de kernel |
| `activation_bypass_from_device` | Bypass de ativação |
| `token_from_device` | Token de autenticação do dispositivo |

### Path Traversal
```
SysContainerDomain-../../../../../../../../. ../Home.app
```
Usado para escapar do sandbox do iOS e acessar diretórios do sistema.

---

## 🔐 Assinatura Digital

### Chave Pública (minisign)
```
untrusted comment: minisign public key: 274AD4DDBD6CAC4D
RWRNrGy93dVKJ4XzbUNPpylwF9JNWkFOBjyxGz/vGlRp6q2nzo39aDQi
```

### Exemplo de Assinatura Tauri (v6.6.0)
```
trusted comment: signature from tauri secret key
timestamp:1778996116  file:Dark Pro Premium_6.6.0_x64_en-US.msi.zip
```

---

## 📁 Estrutura de Arquivos

```
📦 analysis/
├── 📂 src/                          # Dados extraídos do binário
│   ├── .text.bin                    # Código x64 (16 MB)
│   ├── .rdata.bin                   # Dados+strings+payloads (177 MB)
│   ├── arm64_exploit_payload.bin    # Payload checkm8 ARM64 (100 KB)
│   ├── arm64_exploit_disasm.txt     # Disassembly ARM64
│   ├── entry0.txt                   # Entry point
│   ├── winmain.txt                  # WinMain disasm
│   ├── plist_from_bin.txt           # libplist
│   ├── [.data|.edata|.idata|...].bin  # Demais seções PE
│   └── ...
├── 📂 drivers/                      # Drivers USB Windows
│   ├── HFZ_PongoOS_USB_Device.inf
│   ├── HFZ_USB_Device_Driver_DFU_PWNDFU.inf
│   ├── HFZ_USB_Device_Driver_RECOVERY.inf
│   ├── usbaapl64.inf
│   ├── libusb0.dll / libusbK.dll
│   └── ...
├── 📂 report/                       # Relatórios e documentação
│   ├── index.html                   # Documentação interativa (abrir no navegador)
│   ├── exploit_analysis.md          # Relatório em Markdown
│   ├── imports.txt / exports.txt    # DLLs importadas/exportadas
│   └── ...
├── 📂 tools/                        # Ferramentas (reinstalar após clonar)
│   └── custom_scripts/
│       ├── ExportDecompiled.java    # Script Ghidra
│       └── run_decompile.bat        # Launcher Ghidra headless
└── Dark Pro Premium.exe            # Binário alvo (228 MB)
```

---

## 🛠️ Ferramentas Utilizadas

| Ferramenta | Versão | Uso |
|-----------|--------|-----|
| Rizin / rz-find | 0.8.2 | Análise binária, busca de strings |
| Cutter | 2.5.0 | Interface gráfica rizin |
| Ghidra | 11.1.2 | Decompilação (JDK 17) |
| Tauri | 1.8.3 | Framework do app identificado |
| PowerShell | 5.1 | Scripts de extração |

---

## 📊 Timeline da Análise

1. **Identificação**: Executável nativo x64 (não .NET), 12 seções PE, libplist embutida
2. **Extração**: 11 seções PE extraídas como .bin
3. **Payload ARM64**: checkm8 descoberto no .rdata (~14,8 MB), 100 KB de código ARM64 válido
4. **Servidor**: `isalldone.com.br` identificado e confirmado como ativo
5. **Framework**: App identificado como Tauri 1.8.3 (Rust + WebView2)
6. **Falso Marketing**: iOS 17–26 ausentes do binário — comprovadamente falsos
7. **Módulos**: Mapeados módulos flashceld (auth, commands, device_commands, etc.)

---

## ⚠️ Aviso Legal

Esta análise é realizada **exclusivamente para fins educacionais e de pesquisa em segurança**. O material aqui documentado destaca técnicas de engenharia reversa aplicadas a um software comercial para expor falsas alegações de marketing. Não incentivamos o uso indevido destas informações.

---

## 🔗 Links Úteis

- [palera1n (projeto original)](https://github.com/palera1n/palera1n)
- [checkra1n](https://checkra.in)
- [Tauri Framework](https://tauri.app)
- [checkm8 (CVE-2019-8791)](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8791)

---

*Documento gerado em 24/07/2026 · Análise forense completa por Aycher & AI assistant*
