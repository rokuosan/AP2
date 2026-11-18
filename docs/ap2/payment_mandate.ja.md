# Payment Mandate

Payment Mandate は、特定のチェックアウトに対する支払いを認可するための Mandate です。

## 用途

Shopping Agent が Payment Mandate の内容を作成し、Trusted Surface がユーザーに表示します。Credential Provider、決済ネットワーク、Merchant Payment Processor が検証します。

## 型

クローズドな Payment Mandate の `vct` クレームには `mandate.payment.1`、オープンな Payment Mandate には `mandate.payment.open.1` を指定しなければなりません。バージョン接尾辞の仕組みは[Mandate のバージョン](specification.md)を参照してください。

## Mandate スキーマ

クローズドな Payment Mandate は次のスキーマに適合します。

{{ schema_fields('payment_mandate', 'ap2', show_sd=True) }}

オープンな Payment Mandate には、クローズドな Payment Mandate のプロパティを任意で含められます。

### Payment Mandate の制約

この文書では Payment Mandate に次の制約を定義します。

- **エージェントの反復利用**：エージェントが Payment Mandate を複数回使う条件を定めます。
- **許可された受取人**：受取人を候補となる販売者のいずれかに制限します。
- **許可された支払い手段**：支払い手段を候補のいずれかに制限します。
- **許可された Payment Initiation Service Provider（PISP）**：PISP を候補のいずれかに制限します。
- **金額範囲**：金額の範囲を制限します。
- **予算**：総額の上限を定めます。エージェントの反復利用制約とともに使います。
- **参照**：Payment Mandate を対応するオープンな Checkout Mandate と、そこから連鎖する Checkout Mandate に結び付けます。
- **実行日**：実行日を特定の範囲に制限します。

### エージェントの反復利用

**型**：`payment.agent_recurrence`

**説明**：エージェントが Payment Mandate を複数回利用する条件を定めます。

**プロパティ**：

{{ schema_fields('open_payment_mandate', 'ap2', show_sd=True, pointer='#/$defs/agent_recurrence') }}

**評価**：予算を評価するには、このオープンな Mandate に関連付けられた Payment Mandate の過去の提示を追跡する必要があります。今回の Payment Mandate が `frequency` の定義を満たすだけの時間を前回の提示から空けており、`max_occurrences` が今回の利用回数以上であれば、この制約を満たします。

**例**

```json
{
  "type": "payment.agent_recurrence",
  "frequency": "MONTHLY",
  "max_occurrences": 12
}
```

### 許可された受取人

**型**：`payment.allowed_payees`

**説明**：この Payment Mandate で許可する受取人の集合を定めます。

**プロパティ**：

{{ schema_fields('open_payment_mandate', 'ap2', show_sd=True, pointer='#/$defs/allowed_payees') }}

**評価**：Payment Mandate の `payee` プロパティが `allowed` 配列に含まれていなければなりません。

**例**

```json
{
  "type": "payment.allowed_payees",
  "allowed": [
    {"name": "Merchant Choice", "website": "https://merchant-choice.com"}
  ]
}
```

### 許可された支払い手段

**型**：`payment.allowed_payment_instruments`

**説明**：この Payment Mandate で許可する支払い手段の集合を定めます。

**プロパティ**：

{{ schema_fields('open_payment_mandate', 'ap2', show_sd=True, pointer='#/$defs/allowed_payment_instruments') }}

**評価**：Payment Mandate の `payment_instrument` プロパティが `allowed` 配列に含まれていなければなりません。

**例**

```json
{
  "type": "payment.allowed_payment_instruments",
  "allowed": [
    {"id": "abe3c...", "type": "card", "description": "network ··· 1234"},
    {"id": "zde4d...", "type": "UPI", "description": "user****@bankname"}
  ]
}
```

### 許可された Payment Initiation Service Provider（PISP）

**型**：`payment.allowed_pisps`

**説明**：取引を仲介できる PISP の集合を定めます。

**プロパティ**：

{{ schema_fields('open_payment_mandate', 'ap2', show_sd=True, pointer='#/$defs/allowed_pisps') }}

**評価**：取引を仲介する PISP が `allowed` 配列に含まれていなければなりません。

**例**

```json
{
  "type": "payment.allowed_pisps",
  "allowed": [
    {"legal_name": "Example Payment Services Ltd.", "brand_name": "ExamplePay", "domain_name": "examplepay.com"}
  ]
}
```

### 金額範囲

**型**：`payment.amount_range`

**説明**：最終金額の有効範囲を定めます。

**プロパティ**：

{{ schema_fields('open_payment_mandate', 'ap2', show_sd=True, pointer='#/$defs/amount_range') }}

**評価**：Payment Mandate の `payment_amount` は `min` と `max` の範囲内でなければなりません。Payment Mandate の `currency` はこの制約の `currency` と一致しなければなりません。

### 予算

**型**：`payment.budget`

**説明**：反復利用における支払い総額の上限を定めます。

**プロパティ**：

{{ schema_fields('open_payment_mandate', 'ap2', show_sd=True, pointer='#/$defs/budget') }}

**評価**：この Payment Mandate を使った累計支出を追跡します。今回の要求額と過去のクローズドな Payment Mandate の金額合計が `max` 以下であれば制約を満たします。承認後、今回の金額を累計に加え、次回の評価に使います。

### 参照

**型**：`payment.reference`

**説明**：Payment Mandate をオープンな Checkout Mandate と、その Checkout Mandate から連鎖する Checkout に関連付けます。

**プロパティ**：

{{ schema_fields('open_payment_mandate', 'ap2', show_sd=True, pointer='#/$defs/reference') }}

**評価**：承認対象の Checkout Mandate の委任チェーンに、ハッシュが一致するオープンな Checkout Mandate が含まれていなければなりません。ハッシュアルゴリズムは、この制約を含む SD-JWT の `_sd_alg` と同じものを使います。指定がなければ `sha-256` を使います。

### 実行日

**型**：`payment.execution_date`

**説明**：支払いの実行可能な日付範囲を定めます。

**プロパティ**：

{{ schema_fields('open_payment_mandate', 'ap2', show_sd=True, pointer='#/$defs/execution_date') }}

**評価**：Payment Mandate の `execution_date` は、`not_before` があればその日時以降、`not_after` があればその日時以前でなければなりません。

## Payment Receipt

Payment Receipt は次のスキーマに適合します。

{{ schema_fields('payment_receipt', 'ap2', show_sd=True) }}

## 例

### 開いた Payment Mandate の SD-JWT と開示情報

オープンな Payment Mandate と開示情報を SD-JWT で表します。JSON のクレーム、プロパティ名、値はプロトコル上のデータのため原文のままです。

### 閉じた Payment Mandate の SD-JWT と開示情報

クローズドな Payment Mandate は特定の支払いを認可し、Checkout に結び付けられます。

### オープン Mandate に連結したクローズド Mandate

委任された SD-JWT の処理後、オープンな Payment Mandate にクローズドな Payment Mandate を連結できます。

## 共通型

### Amount

金額と通貨を表します。

### Merchant

販売者を識別する情報を表します。

### PaymentInstrument

支払い手段を表します。

### Pisp

Payment Initiation Service Provider を表します。


## 原文のデータ例

以下に示す JSON は、原文に掲載されたサンプルです。プロトコルの値と構造を保つため、フィールド名や値は翻訳していません。

### サンプル 1

```json
{
  "type": "payment.agent_recurrence",
  "frequency": "MONTHLY",
  "max_occurrences": 12
}
```

### サンプル 2

```json
{
  "type": "payment.allowed_payees",
  "allowed": [
    {
      "name": "Merchant Choice",
      "website": "https://merchant-choice.com"
    }
  ]
}
```

### サンプル 3

```json
{
  "type": "payment.allowed_payment_instruments",
  "allowed": [
    {
      "id": "abe3c...",
      "type": "card",
      "description": "network ··· 1234"
    },
    {
      "id": "zde4d...",
      "type": "UPI",
      "description": "user****@bankname"
    },
  ]
}
```

### サンプル 4

```json
{
  "type": "payment.allowed_pisps",
  "allowed": [
    {
      "legal_name": "Example Payment Services Ltd.",
      "brand_name": "ExamplePay",
      "domain_name": "examplepay.com"
    }
  ]
}
```

### サンプル 5

```json
{
  "type": "payment.amount_range",
  "max": 100.50,
  "min": 10.00,
  "currency": "USD"
}
```

### サンプル 6

```json
{
  "type": "payment.budget",
  "max": 1000.00,
  "currency": "USD"
}
```

### サンプル 7

```json
{
  "type": "payment.reference",
  "conditional_transaction_id": "A4wG4B..."
}
```

### サンプル 8

```json
{
  "type": "payment.execution_date",
  "not_before": "2026-03-31T00:00:00Z",
  "not_after": "2026-04-30T23:59:59Z"
}
```

### サンプル 9

```json
{
  "issuer_signed_jwt": {
    "header": {
      "alg": "ES256",
      "typ": "example+sd-jwt",
      "kid": "agent-provider-key-1"
    },
    "payload": {
      "delegate_payload": [
        {
          "...": "3YRtZ-lBNhI_YhggShrdHhrSuDPSpwMvJ3VWjUnhDQM"
        }
      ],
      "_sd_alg": "sha-256"
    }
  },
  "disclosures": [
    {
      "digest": "oEH7i1gyb-zn6awwjy57LvzxkQDfD-8tvlC2XuIkgOA",
      "decoded": [
        "s9WPt2U4GapcJsonyEb6bjg",
        {
          "id": "merchant_1",
          "name": "Demo Merchant",
          "website": "https://demo-merchant.example"
        }
      ]
    },
    {
      "digest": "3YRtZ-lBNhI_YhggShrdHhrSuDPSpwMvJ3VWjUnhDQM",
      "decoded": [
        "ZtKS5FSrIAY6HlGB4Ho7mg",
        {
          "vct": "mandate.payment.open.1",
          "constraints": [
            {
              "type": "payment.amount_range",
              "currency": "USD",
              "max": 20000,
              "min": 0
            },
            {
              "type": "payment.allowed_payees",
              "allowed": [
                {
                  "...": "oEH7i1gyb-zn6awwjy57LvzxkQDfD-8tvlC2XuIkgOA"
                }
              ]
            },
            {
              "type": "payment.reference",
              "conditional_transaction_id": "FzLoxbbtgQGYZxoSM2NJYJtkFTSsdfUBoVEQ12k7JN8"
            }
          ],
          "cnf": {
            "jwk": {
              "crv": "P-256",
              "kty": "EC",
              "x": "QpSyxPQHy38xckypDr54gZ3T42zj9iLtV4koyb5U27c",
              "y": "37HLd7JJinxjJIn8J7HijssoeclbfhdW-gUL7feI9lw"
            }
          },
          "iat": 1777342357,
          "exp": 1777345957
        }
      ]
    }
  ]
}
```

### サンプル 10

```
eyJhbGciOiAiRVMyNTYiLCAidHlwIjogImV4YW1wbGUrc2Qtand0IiwgImtpZCI6ICJhZ2VudC1wcm92aWRlci1rZXktMSJ9.eyJkZWxlZ2F0ZV9wYXlsb2FkIjogW3siLi4uIjogIjNZUnRaLWxCTmhJX1loZ2dTaHJkSGhyU3VEUFNwd012SjNWV2pVbmhEUU0ifV0sICJfc2RfYWxnIjogInNoYS0yNTYifQ.ZQ_5x2hYLusuUNAA2OJloeS2w3fxZRCsSvcU-wg9fK7nlMmsbpK6EPlntD8oHq5waegxsLmSL51V5hfyaQViMg~WyJzOVdQdDJVNEdhcGNKc255RWI2YmpnIiwgeyJpZCI6ICJtZXJjaGFudF8xIiwgIm5hbWUiOiAiRGVtbyBNZXJjaGFudCIsICJ3ZWJzaXRlIjogImh0dHBzOi8vZGVtby1tZXJjaGFudC5leGFtcGxlIn1d~WyJadEtTNUZTcklBWTZIbEdCNEhvN21nIiwgeyJ2Y3QiOiAibWFuZGF0ZS5wYXltZW50Lm9wZW4uMSIsICJjb25zdHJhaW50cyI6IFt7InR5cGUiOiAicGF5bWVudC5hbW91bnRfcmFuZ2UiLCAiY3VycmVuY3kiOiAiVVNEIiwgIm1heCI6IDIwMDAwLCAibWluIjogMH0sIHsidHlwZSI6ICJwYXltZW50LmFsbG93ZWRfcGF5ZWVzIiwgImFsbG93ZWQiOiBbeyIuLi4iOiAib0VIN2kxZ3liLXpuNmF3d2p5NTdMdnp4a1FEZkQtOHR2bEMyWHVJa2dPQSJ9XX0sIHsidHlwZSI6ICJwYXltZW50LnJlZmVyZW5jZSIsICJjb25kaXRpb25hbF90cmFuc2FjdGlvbl9pZCI6ICJGekxveGJidGdRR1laeG9TTTJOSllKdGtGVFNzZGZVQm9WRVExMms3Sk44In1dLCAiY25mIjogeyJqd2siOiB7ImNydiI6ICJQLTI1NiIsICJrdHkiOiAiRUMiLCAieCI6ICJRcFN5eFBRSHkzOHhja3l2RHI1NGdaM1Q0MnpqOWlMdFY0a295YjVVMjdjIiwgInkiOiAiMzdITGQ3SkppbnhqSkluOEo3SGlqc3NvZWNCbGZoZFctZ1VMN2ZlSTlsdyJ9fSwgImlhdCI6IDE3NzczNDIzNTcsICJleHAiOiAxNzc3MzQ1OTU3fV0~
```

### サンプル 11

```json
{
  "issuer_signed_jwt": {
    "header": {
      "alg": "ES256",
      "typ": "kb+sd-jwt"
    },
    "payload": {
      "delegate_payload": [
        {
          "...": "G2DuU6IjyDkD-9ItStdsUo48C5uJqDs1E9Hf5GT3TgM"
        }
      ],
      "iat": 1777342370,
      "aud": "credential-provider",
      "nonce": "a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3",
      "sd_hash": "uixoHemmfrrCSbPREo9j-ziLuMkqExsPeWrwA-PK0Ck",
      "_sd_alg": "sha-256"
    }
  },
  "disclosures": [
    {
      "digest": "G2DuU6IjyDkD-9ItStdsUo48C5uJqDs1E9Hf5GT3TgM",
      "decoded": [
        "FW6McBJImqODuhQlpI4Idw",
        {
          "vct": "mandate.payment.1",
          "transaction_id": "NivWhuqfzcvZNapvIEJ2-3tsdQLkiuIcye2g46WVgX8",
          "payee": {
            "id": "merchant_1",
            "name": "Demo Merchant",
            "website": "https://demo-merchant.example"
          },
          "payment_amount": {
            "amount": 19900,
            "currency": "USD"
          },
          "payment_instrument": {
            "id": "stub",
            "type": "card",
            "description": "Card ••••4242"
          }
        }
      ]
    }
  ]
}
```

### サンプル 12

```
eyJhbGciOiAiRVMyNTYiLCAidHlwIjogImtiK3NkLWp3dCJ9.eyJkZWxlZ2F0ZV9wYXlsb2FkIjogW3siLi4uIjogIkcyRHVVNklqeURrRC05SXRTdGRzVW80OEM1dUpxRHMxRTlIZjVHVDNUZ00ifV0sICJpYXQiOiAxNzc3MzQyMzcwLCAiYXVkIjogImNyZWRlbnRpYWwtcHJvdmlkZXIiLCAibm9uY2UiOiAiYThiN2M2ZDVlNGYzYTJiMWMwZDllOGY3YTZiNWM0ZDMiLCAic2RfaGFzaCI6ICJ1aXhvSGVtbWZyckNTYlBSRW85ai16aUx1TWtxRXhzUGVXcndBLVBLMENrIiwgIl9zZF9hbGciOiAic2hhLTI1NiJ9.TgI6w9zeL993uzAYE9fnAJXjnrpliDY5DpDKTSQoioH3msapVIz0Ex23ncQXwmsSmT3xOqkSpigQD1EYKck-dQ~WyJmVzZNY0JKSW1xT0R1aFFscEk0SWR3IiwgeyJ2Y3QiOiAibWFuZGF0ZS5wYXltZW50LjEiLCAidHJhbnNhY3Rpb25faWQiOiAiTml2V2h1cWZ6Y3ZaTmFwdklFSjItM3RzZFFMa2l1SWN5ZTJnNDZXVmdYOCIsICJwYXllZSI6IHsiaWQiOiAibWVyY2hhbnRfMSIsICJuYW1lIjogIkRlbW8gTWVyY2hhbnQiLCAid2Vic2l0ZSI6ICJodHRwczovL2RlbW8tbWVyY2hhbnQuZXhhbXBsZSJ9LCAicGF5bWVudF9hbW91bnQiOiB7ImFtb3VudCI6IDE5OTAwLCAiY3VycmVuY3kiOiAiVVNEIn0sICJwYXltZW50X2luc3RydW1lbnQiOiB7ImlkIjogInN0dWIiLCAidHlwZSI6ICJjYXJkIiwgImRlc2NyaXB0aW9uIjogIkNhcmQgXHUyMDIyXHUyMDIyXHUyMDIyNDI0MiJ9fV0~
```

### サンプル 13

```json
{
  "issuer_signed_jwt": {
    "header": {
      "alg": "ES256",
      "typ": "example+sd-jwt",
      "kid": "agent-provider-key-1"
    },
    "payload": {
      "delegate_payload": [
        {
          "...": "3YRtZ-lBNhI_YhggShrdHhrSuDPSpwMvJ3VWjUnhDQM"
        }
      ],
      "_sd_alg": "sha-256"
    }
  },
  "disclosures": [
    {
      "digest": "oEH7i1gyb-zn6awwjy57LvzxkQDfD-8tvlC2XuIkgOA",
      "decoded": [
        "s9WPt2U4GapcJsonyEb6bjg",
        {
          "id": "merchant_1",
          "name": "Demo Merchant",
          "website": "https://demo-merchant.example"
        }
      ]
    },
    {
      "digest": "3YRtZ-lBNhI_YhggShrdHhrSuDPSpwMvJ3VWjUnhDQM",
      "decoded": [
        "ZtKS5FSrIAY6HlGB4Ho7mg",
        {
          "vct": "mandate.payment.open.1",
          "constraints": [
            {
              "type": "payment.amount_range",
              "currency": "USD",
              "max": 20000,
              "min": 0
            },
            {
              "type": "payment.allowed_payees",
              "allowed": [
                {
                  "...": "oEH7i1gyb-zn6awwjy57LvzxkQDfD-8tvlC2XuIkgOA"
                }
              ]
            },
            {
              "type": "payment.reference",
              "conditional_transaction_id": "FzLoxbbtgQGYZxoSM2NJYJtkFTSsdfUBoVEQ12k7JN8"
            }
          ],
          "cnf": {
            "jwk": {
              "crv": "P-256",
              "kty": "EC",
              "x": "QpSyxPQHy38xckypDr54gZ3T42zj9iLtV4koyb5U27c",
              "y": "37HLd7JJinxjJIn8J7HijssoeclbfhdW-gUL7feI9lw"
            }
          },
          "iat": 1777342357,
          "exp": 1777345957
        }
      ]
    }
  ]
}
{
  "issuer_signed_jwt": {
    "header": {
      "alg": "ES256",
      "typ": "kb+sd-jwt"
    },
    "payload": {
      "delegate_payload": [
        {
          "...": "G2DuU6IjyDkD-9ItStdsUo48C5uJqDs1E9Hf5GT3TgM"
        }
      ],
      "iat": 1777342370,
      "aud": "credential-provider",
      "nonce": "a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3",
      "sd_hash": "uixoHemmfrrCSbPREo9j-ziLuMkqExsPeWrwA-PK0Ck",
      "_sd_alg": "sha-256"
    }
  },
  "disclosures": [
    {
      "digest": "G2DuU6IjyDkD-9ItStdsUo48C5uJqDs1E9Hf5GT3TgM",
      "decoded": [
        "FW6McBJImqODuhQlpI4Idw",
        {
          "vct": "mandate.payment.1",
          "transaction_id": "NivWhuqfzcvZNapvIEJ2-3tsdQLkiuIcye2g46WVgX8",
          "payee": {
            "id": "merchant_1",
            "name": "Demo Merchant",
            "website": "https://demo-merchant.example"
          },
          "payment_amount": {
            "amount": 19900,
            "currency": "USD"
          },
          "payment_instrument": {
            "id": "stub",
            "type": "card",
            "description": "Card ••••4242"
          }
        }
      ]
    }
  ]
}
```

### サンプル 14

```
eyJhbGciOiAiRVMyNTYiLCAidHlwIjogImV4YW1wbGUrc2Qtand0IiwgImtpZCI6ICJhZ2VudC1wcm92aWRlci1rZXktMSJ9.eyJkZWxlZ2F0ZV9wYXlsb2FkIjogW3siLi4uIjogIjNZUnRaLWxCTmhJX1loZ2dTaHJkSGhyU3VEUFNwd012SjNWV2pVbmhEUU0ifV0sICJfc2RfYWxnIjogInNoYS0yNTYifQ.ZQ_5x2hYLusuUNAA2OJloeS2w3fxZRCsSvcU-wg9fK7nlMmsbpK6EPlntD8oHq5waegxsLmSL51V5hfyaQViMg~WyJzOVdQdDJVNEdhcGNKc255RWI2YmpnIiwgeyJpZCI6ICJtZXJjaGFudF8xIiwgIm5hbWUiOiAiRGVtbyBNZXJjaGFudCIsICJ3ZWJzaXRlIjogImh0dHBzOi8vZGVtby1tZXJjaGFudC5leGFtcGxlIn1d~WyJadEtTNUZTcklBWTZIbEdCNEhvN21nIiwgeyJ2Y3QiOiAibWFuZGF0ZS5wYXltZW50Lm9wZW4uMSIsICJjb25zdHJhaW50cyI6IFt7InR5cGUiOiAicGF5bWVudC5hbW91bnRfcmFuZ2UiLCAiY3VycmVuY3kiOiAiVVNEIiwgIm1heCI6IDIwMDAwLCAibWluIjogMH0sIHsidHlwZSI6ICJwYXltZW50LmFsbG93ZWRfcGF5ZWVzIiwgImFsbG93ZWQiOiBbeyIuLi4iOiAib0VIN2kxZ3liLXpuNmF3d2p5NTdMdnp4a1FEZkQtOHR2bEMyWHVJa2dPQSJ9XX0sIHsidHlwZSI6ICJwYXltZW50LnJlZmVyZW5jZSIsICJjb25kaXRpb25hbF90cmFuc2FjdGlvbl9pZCI6ICJGekxveGJidGdRR1laeG9TTTJOSllKdGtGVFNzZGZVQm9WRVExMms3Sk44In1dLCAiY25mIjogeyJqd2siOiB7ImNydiI6ICJQLTI1NiIsICJrdHkiOiAiRUMiLCAieCI6ICJRcFN5eFBRSHkzOHhja3l2RHI1NGdaM1Q0MnpqOWlMdFY0a295YjVVMjdjIiwgInkiOiAiMzdITGQ3SkppbnhqSkluOEo3SGlqc3NvZWNCbGZoZFctZ1VMN2ZlSTlsdyJ9fSwgImlhdCI6IDE3NzczNDIzNTcsICJleHAiOiAxNzc3MzQ1OTU3fV0~~eyJhbGciOiAiRVMyNTYiLCAidHlwIjogImtiK3NkLWp3dCJ9.eyJkZWxlZ2F0ZV9wYXlsb2FkIjogW3siLi4uIjogIkcyRHVVNklqeURrRC05SXRTdGRzVW80OEM1dUpxRHMxRTlIZjVHVDNUZ00ifV0sICJpYXQiOiAxNzc3MzQyMzcwLCAiYXVkIjogImNyZWRlbnRpYWwtcHJvdmlkZXIiLCAibm9uY2UiOiAiYThiN2M2ZDVlNGYzYTJiMWMwZDllOGY3YTZiNWM0ZDMiLCAic2RfaGFzaCI6ICJ1aXhvSGVtbWZyckNTYlBSRW85ai16aUx1TWtxRXhzUGVXcndBLVBLMENrIiwgIl9zZF9hbGciOiAic2hhLTI1NiJ9.TgI6w9zeL993uzAYE9fnAJXjnrpliDY5DpDKTSQoioH3msapVIz0Ex23ncQXwmsSmT3xOqkSpigQD1EYKck-dQ~WyJmVzZNY0JKSW1xT0R1aFFscEk0SWR3IiwgeyJ2Y3QiOiAibWFuZGF0ZS5wYXltZW50LjEiLCAidHJhbnNhY3Rpb25faWQiOiAiTml2V2h1cWZ6Y3ZaTmFwdklFSjItM3RzZFFMa2l1SWN5ZTJnNDZXVmdYOCIsICJwYXllZSI6IHsiaWQiOiAibWVyY2hhbnRfMSIsICJuYW1lIjogIkRlbW8gTWVyY2hhbnQiLCAid2Vic2l0ZSI6ICJodHRwczovL2RlbW8tbWVyY2hhbnQuZXhhbXBsZSJ9LCAicGF5bWVudF9hbW91bnQiOiB7ImFtb3VudCI6IDE5OTAwLCAiY3VycmVuY3kiOiAiVVNEIn0sICJwYXltZW50X2luc3RydW1lbnQiOiB7ImlkIjogInN0dWIiLCAidHlwZSI6ICJjYXJkIiwgImRlc2NyaXB0aW9uIjogIkNhcmQgXHUyMDIyXHUyMDIyXHUyMDIyNDI0MiJ9fV0~
```
