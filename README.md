# Folder_as_HTML
Webová aplikace zobrazují obsah složky "content",kterou si může uživatel sám nastavit.

## Podporované operační systémy
- Windows :window:
    - Windows 10
    - Windows 11
- Linux :penguin:
    - Raspbian

## Konfigurace


| název konfigurace  | hodnota                                                |
|--------------------|--------------------------------------------------------|
| ip_address         | ip adresa, na které bude aplikace běžet                |
| port               | port, na které bude aplikace běžet                     |
| debug              | boolovská hodnota, jestli má být aplikace v debug módu |
| content_root       | absolutní cesta, ke složce, kterou chcete scílet       |

```
{
    "ip_address":"0.0.0.0",
    "port":5000,
    "debug":false,
    "content_root":""
}
```