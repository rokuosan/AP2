# Agent Authorization（エージェント認可）

> このページは AP2 ドキュメントの非公式日本語訳です。
> [英語の原文を読む](https://github.com/google-agentic-commerce/AP2/blob/main/docs/ap2/agent_authorization.md)

エージェントは処理が非決定論的であるため、適切に動作する場合でも、人間向けの通常の認可モデルより厳密に動作を制約する必要があります。

この文書では、ユーザーがエージェントに何を許可したかを最終的な検証者が明確に確認できるよう、エージェント認可のモデルを定めます。AP2 は支払いにこのモデルを使いますが、将来はほかの用途にも適用できます。

認可は次の2段階で行います。

- **Mandate の委任**：ユーザーが Trusted Surface 上で Mandate の内容を承認し、作成された Mandate をエージェントに委任します。
- **アクションの認可**：検証者は、ユーザーに代わって操作する権限の証明をエージェントに求めます。エージェントは該当する Mandate を提示し、処理後に検証者から Receipt を受け取ります。

<div style="display: flex; justify-content: space-around;" markdown="1">
  <figure markdown="span">
    ![Mandate 委任の概要図](../assets/mandate_delegation_overview.svg){ style="width:100%" }
    <figcaption align="center">Mandate の委任</figcaption>
  </figure>
  <figure markdown="span">
    ![アクション認可の概要図](../assets/action_authorization_overview.svg){ style="width:100%" }
    <figcaption align="center">アクションの認可</figcaption>
  </figure>
</div>

## Mandate の委任

Mandate の委任は次のように行います。

- エージェントはユーザーに承認してもらう Mandate の内容を作成します。
- Trusted Surface 上でユーザーに Mandate の内容を表示します。
- ユーザーの承認と同意を得た後、Mandate を作成してエージェントに返します。
- エージェントは Mandate を保存し、後で利用します。

この文書では、Mandate の委任方法として User Credential と Trusted Agent Provider の2つを定義します。

User Credential 方式では、エージェントの外部にある発行者を検証者が信頼し、その発行者が Trusted Surface の適切性を保証します。1つの User Credential で複数のエージェントに Mandate を委任でき、検証者は各エージェントとの個別の信頼関係を確立する必要がありません。

Trusted Agent Provider 方式では、検証者が Agent Provider を信頼します。信頼モデルは簡潔になりますが、検証者は各 Agent Provider との信頼関係を確立する必要があります。Agent Provider が User Credential の発行者も兼ね、両方式を組み合わせることもできます。

> 注：将来、委任された Mandate の完全性を確立する別の方法を検討できます。Mandate の内容は、その完全性を確立する方法に依存しません。完全な資格情報を使わず、パスキーやハードウェアで証明された鍵など、ユーザー鍵を直接信頼する方式も考えられます。

### User Credential

この方式には、User Credential の発行者、資格情報を保持する Trusted Surface、エージェントの3者が関わります。検証者は発行者を信頼し、適切なユーザーの同意と認可を得た後でのみ Trusted Surface が Mandate を作成することを保証します。

<figure markdown="span">
  ![User Credential を使う Mandate 委任](../assets/mandate_delegation_user_credential.svg){ style="width:100%" }
  <figcaption align="center">User Credential による Mandate 委任</figcaption>
</figure>

このフローの前に、発行者は Holder に User Credential を発行します。発行方法はこの文書の対象外です。標準的な方法の一例として [OpenID4VCI](#references) があります。

この方式では、ユーザーの VDC を提示する処理の一部として Mandate を作成し、委任します。

> 注：この文書では SD-JWT VC と OpenID4VP を指定していますが、[ISO mDocs（ISO 18013-5）](#references) などの VDC 形式や [18013-7 Annex C](#references) などのプロトコルも同じ役割を担えます。

#### OpenID4VP による委任

[OpenID4VP](#references) は、Holder が Verifier に VDC を提示する標準プロトコルです。`transaction_data` 機能を使うと、デジタル資格情報の Holder が追加情報を承認し、署名できます。

OpenID4VP で User Credential を使って Mandate を委任するには、エージェントが Authorization Request を作成します。`transaction_data` 配列には、base64url エンコードした JSON オブジェクトを含めます。Mandate 委任オブジェクトには、エンコード前に次のプロパティを含めなければなりません。

- **type**：必須です。値は文字列 `delegate` です。
- **format**：必須です。返却する Mandate の VDC 形式です。
- **delegate_payload**：必須です。Mandate の内容を表す JSON オブジェクトの配列です。
- **delegate_disclosures**：任意です。`delegate_payload` 内の選択的開示情報を含む配列です。

Authorization Response を作成する際は、`delegate_payload` を Key Binding に含めなければなりません。詳細は [Delegate SD-JWT](#references) を参照してください。

DCQL クエリで必要な User Credential を指定するなど、Authorization Request のほかのフィールドは通常どおり設定できます。

利用できる場合は、セキュリティとユーザー体験を高めるため、OpenID4VP による委任に Digital Credentials API を使うことを推奨します。

以下は Checkout Mandate と Payment Mandate を委任する OpenID4VP Authorization Request の参考例です。
読みやすさのため、base64url エンコード文字列の一部を省略しています。

```json
{
  "requests": [
    {
      "protocol": "openid4vp-v1-unsigned",
      "data": {
        "response_type": "vp_token",
        "response_mode": "dc_api",
        "nonce": "b5d4e074-dff5-4cd5-a506-f09dd6f2e33a",
        "dcql_query": {
          "credentials": [
            {
              "id": "dpc_credential",
              "format": "dc+sd-jwt",
              "meta": {
                "vct_values": ["com.emvco.dpc"]
              },
              "claims": [
                { "path": ["card_last_four"] },
                { "path": ["card_network_code"] },
                { "path": ["credential_id"] }
              ]
            }
          ]
        },
        "transaction_data": [
          "eyJ0eXBlIjoicGF5bWVudF9jYXJkIiwiY3JlZ...<truncated_payment_card_base64>...5MDBcIn0ifQ==",
          "eyJ0eXBlIjoiZGVsZWdhdGUiLCJmb3JtYXQiO...<truncated_delegate_base64>...aGEtMjU2Il19"
        ],
        "client_metadata": {
          "client_id_scheme": "x509_san_dns",
          "vp_formats": {
            "dc+sd-jwt": {
              "sd-jwt_alg_values": ["ES256"],
              "kb-jwt_alg_values": ["ES256"]
            }
          }
        }
      }
    }
  ]
}
```

**デコードした `transaction_data` のペイロード（参考）**

`transaction_data` 配列には、base64url エンコードされた2つの JSON オブジェクトが含まれます。

**インデックス0（支払いカードの UI データ）**は、支払いの承認前にユーザーに表示する確認 UI を定義します。

```json
{
  "type": "payment_card",
  "credential_ids": ["dpc_credential"],
  "transaction_data_hashes_alg": ["sha-256"],
  "merchant_name": "Generic Merchant",
  "amount": "USD 150.00",
  "additional_info": "{\"title\":\"Please confirm your purchase details...\",\"tableHeader\":[\"Name\",\"Qty\",\"Price\",\"Total\"],\"tableRows\":[[\"Adult Holland Lop Rabbit\",\"1\",\"150.00\",\"150.00\"]],\"footer\":\"Your total is 150.00\"}"
}
```

**インデックス1（委任する Mandate）**は、`delegate_payload` を通じて、支払いを特定の Checkout Mandate と Payment Mandate の内容に暗号学的に結び付けます。

```json
{
  "type": "delegate",
  "format": "dc+sd-jwt",
  "credential_ids": ["dpc_credential"],
  "transaction_data_hashes_alg": ["sha-256"],
  "delegate_payload": [
    {
      "vct": "mandate.checkout.1",
      "checkout_jwt": "eyJhbGciOiJFUzI1NiIs...<Merchant_Checkout_JWT>",
      "checkout_hash": "3WiKMabE8NRYJgveUbyAZ3pBqRfPrWwGDbOyvbO1eYA",
      "cnf": {
        "jwk": {
          "kty": "EC",
          "crv": "P-256",
          "use": "sig",
          "x": "c09-Eo2PvuO6VrfzLAxTZXBa3ZWkBaa0pR2jcOYKlw",
          "y": "gRETv5wMvNiZJqckokCyDAjIIEg3Y2m77VryMvS75Ww"
        }
      }
    },
    {
      "vct": "mandate.payment.1",
      "transaction_id": "3WiKMabE8NRYJgveUbyAZ3pBqRfPrWwGDbOyvbO1eYA",
      "payment_amount": { "amount": 15000, "currency": "USD" },
      "payee": {
        "id": "merchant_1",
        "name": "Generic Merchant",
        "website": "https://demo-merchant.example"
      },
      "payment_instrument": {
        "id": "b3f1c8a2-6d4e-4f9a-9e3d-8a7c2f1b9d34",
        "type": "dpc",
        "description": "DPC ···· 4444"
      }
    }
  ]
}
```

以下は、ユーザーが署名した Checkout Mandate と Payment Mandate を含む OpenID4VP Authorization Response の参考例です。
読みやすさのため、長い文字列の一部を省略しています。

```json
{
  "protocol": "openid4vp-v1-unsigned",
  "data": {
    "vp_token": {
      "dpc_credential": [
        "eyJhbGci...<truncated_issuer_jwt>...jA~WyJiWk5w...<truncated_disclosure_1>...Q~WyJCdThH...<truncated_disclosure_2>...Q~WyJNUThs...<truncated_disclosure_3>...Q~eyJ0eXAi...<truncated_key_binding_jwt>...jZ"
      ]
    }
  }
}
```

`dpc_credential` は、各要素を `~` で区切った SD-JWT です。
デコードしたペイロードと開示情報を以下に示します。

**SD-JWT 本体のペイロード（発行者が発行した資格情報）**

```json
{
  "iss": "https://digital-credentials.dev",
  "vct": "com.emvco.dpc",
  "iat": 1683000000,
  "exp": 1883000000,
  "_sd_alg": "sha-256",
  "_sd": [
    "0ygSIMbyCz_SAL7CrZeDg_C3AnqJVgf35I1t1ie0RZs",
    "1ipSejAAw_lASOeNsGbj3R_3MZNRtalgU9MYvc73Z5g",
    "3d_ksLaY7NAyu9PQZodRB4XsqF2jquCsl2avOlnWCn8",
    "PBhW42ATJqcs3_odVhHuTGEDhN7idDmZMLLORR-lAec"
  ],
  "cnf": {
    "jwk": {
      "kty": "EC",
      "crv": "P-256",
      "x": "8jBWriuJBY--u__2jOJfcX4Jj4kEqY4CUX9cf1bQddY",
      "y": "csH2kOGhlemhRRuPUYFKJYZgVqEXQh2JfotRKGRMfLE"
    }
  }
}
```

**選択的開示**

販売者が要求した3つのクレームだけを開示し、残りのフィールドは `_sd` のハッシュで秘匿します。

```json
[
  ["bZNpmTeoL5tYU7gKTVkTUA", "card_last_four", "4444"],
  ["Bu8Gie949nAgBdL6B657Mw", "card_network_code", "ACME"],
  ["MQ8lrNkAwYlavMT8own4DA", "credential_id", "b3f1c8a2-6d4e-4f9a-9e3d-8a7c2f1b9d34"]
]
```

1つの Authorization Request 内で `delegate_payload` 配列に複数の要素を指定し、複数の Mandate を委任することもできます。

### Trusted Agent Provider

この方式では検証者が Agent Provider を直接信頼し、適切なユーザーの同意と認可を得た後でのみ Agent Provider が Mandate を作成することを保証します。事前に発行された資格情報は必要ありません。

<figure markdown="span">
  ![Trusted Agent Provider による Mandate 委任](../assets/mandate_delegation_trusted_agent_provider.svg){ style="width:100%" }
  <figcaption align="center">Trusted Agent Provider による Mandate 委任</figcaption>
</figure>

- エージェントは Mandate の内容を作成し、Agent Provider が管理する Trusted Surface に渡します。たとえば、アプリケーション内の決定論的な別コンポーネントを使います。
- Agent Provider の Trusted Surface は Mandate の内容をユーザーに表示し、必要な承認と同意を取得します。
- Agent Provider は安全に保管された署名鍵で Mandate を作成します。たとえば Trusted Surface から Agent Provider のバックエンドに連絡して署名を依頼します。

Agent Provider は、エージェントが Agent Provider の署名鍵にアクセスできず、Trusted Surface を経由しない限り鍵を使えないようにしなければなりません。リスクの詳細は [セキュリティとプライバシーに関する考慮事項](security_and_privacy_considerations.ja.md) を参照してください。

以下は、Agent Provider が Checkout Mandate を `sd-jwt-vc` ペイロードとして作成する参考例です。

**デコードした最上位のペイロード**

```json
{
  "iss": "https://agent-provider.example.com",
  "vct": "com.example.agent_mandate",
  "iat": 1777326189,
  "_sd_alg": "sha-256",
  "delegate_payload": [
    { "...": "4UrKesfj0IT5_OE7zLYlXHkAwPbC3JvJgIxku3uq0EE" }
  ]
}
```

**デコードした開示情報（オープンな Mandate）**

末尾が `uq0EE` のハッシュに対応する開示情報が、オープンな Mandate を示します。
制約配列に含まれる購入可能な商品と利用可能な販売者も、ハッシュで秘匿されています。

```json
[
  "8rGxzvzfSEW7fw4nb_dYx_w",
  {
    "vct": "mandate.checkout.open.1",
    "cnf": { "jwk": { "crv": "P-256", "kty": "EC", "x": "7MAQoKtK...", "y": "i3OUjGXe..." } },
    "iat": 1777326189,
    "exp": 1777329789,
    "constraints": [
      {
        "type": "checkout.line_items",
        "items": [
          {
            "id": "line_1",
            "quantity": 1,
            "acceptable_items": [
              { "...": "LqZRRzN7nzxJCVf0kP5OvvWvits5CcATHkoq_xGoz8s" }
            ]
          }
        ]
      },
      {
        "type": "checkout.allowed_merchants",
        "allowed": [
          { "...": "UZSGFNQpapJSRQLCeVDfqGzfMCUiJvLL80_kcDai_OI" }
        ]
      }
    ]
  }
]
```

**デコードした開示情報（入れ子の配列の要素）**

エージェントは、上の制約配列で許可された商品の明細と販売者を選択的に開示できます。

```json
[
  "vK5dz2nnVpgtoC9dZy9uHw",
  {
    "id": "supershoe_limited_edition_gold_sneaker_womens_9_0",
    "title": "SuperShoe Limited Edition Gold"
  }
]
```

```json
[
  "NAhMECHMBjd978UDQqsAYA",
  {
    "id": "merchant_1",
    "name": "Demo Merchant",
    "website": "https://demo-merchant.example"
  }
]
```

## Mandate の構造

Mandate は、ユーザーが承認した元の Mandate から、Verifier の操作を認可するクローズドな Mandate までを暗号学的に検証可能な連鎖として構成します。

Mandate には2つの状態があります。

- **クローズド**：Verifier との特定の取引に結び付いており、エージェントの操作を認可します。Agent はオープンな Mandate の `cnf` クレームで指定された鍵を使い、Key Binding JWT（Proof-of-Possession）を生成します。
- **オープン**：まだ特定の取引に結び付いていません。クローズドな Mandate に記載できる内容の制約を持ち、その Mandate を使える特定の Agent に結び付いています。

オープンな Mandate を使うことで、ユーザーが不在の間もエージェントは自律的に操作できます。同時に、その動作を適切な範囲に制限できます。

<figure markdown="span">
  ![オープンとクローズドな Mandate の連鎖例](../assets/mandate_chain_example.svg){ style="width:800px" }
  <figcaption align="center">Mandate の連鎖例</figcaption>
</figure>

図は、同じ操作（A を使った doX）をユーザーが認可する2つの例を示します。「人が参加する」場合、ユーザーがクローズドな Mandate の内容に直接署名します。もう一方では、ユーザーがオープンな Mandate の内容に署名し、エージェントがユーザーに代わってクローズドな Mandate に署名します。認可を示すため、エージェントは Mandate の連鎖全体を提示します。

オープンな Mandate は利用前に特定の取引に結び付ける必要があるため、暗号学的な Key Binding に対応しなければなりません。

### SD-JWT VC を使う Mandate

[SD-JWT](#references) は JSON を暗号学的に保護し、Mandate に役立つ機能を提供します。Key Binding によってユーザー不在時にエージェントが所有証明と取引への結び付きを示せます。また、選択的開示で制約のうち適用対象だけを開示し、ユーザーのプライバシーを守りながらエージェントに判断の柔軟性を持たせられます。

> 注：この文書では SD-JWT VC を使いますが、ISO mDocs などの VDC も利用できます。

SD-JWT の Mandate Content には次のクレームを含みます。

- `vct`：必須です。資格情報の型に加えて Mandate の型を一意に識別する文字列です。
- `constraints`：任意です。クローズドな Mandate に含められる内容を制約する、拡張可能なオブジェクトの配列です。各制約には一意な `type` が必須で、その他のプロパティは制約の型によって異なります。
- `cnf`：任意です。[RFC 7800](#references) で定義される Proof-of-Possession 鍵の確認方法を含みます。Mandate がオープンな場合は必須です。

Mandate の型に応じて、ほかのプロパティも含められます。オープンな Mandate は、対象型の必須フィールドをすべて持つ必要はありませんが、最終的なクローズドな Mandate には必須フィールドを含めなければなりません。SD-JWT VC の任意のクレームも利用できます。

AP2 仕様では支払い用の Mandate 型と制約型を定めます。別の用途向けに新たな型を定義することもできます。名前の衝突を避けるため、定義主体が管理する rDNS プレフィックスや適切な URN など、衝突耐性のある命名方法を推奨します。

#### 検証と処理の規則 { #verification-and-processing-rules }

SD-JWT Mandate の連鎖は次の規則に従って検証し、処理します。

1. [Delegate SD-JWT](#references) に従って SD-JWT の連鎖を検証し、処理します。
2. オープンな Mandate の内容からクレームを抽出し、クローズドな Mandate の内容に同じ値が変更されずに含まれていることを確認します。
3. 各オープンな Mandate の内容から制約をすべて抽出し、制約型に従ってクローズドな Mandate の内容と照合します。未知の制約は評価失敗として扱わなければなりません。

## アクションの認可

アクションの認可は Agent と Verifier の間で行います。購入の実行など、特定の操作に適切な認可があることを Agent に証明させる必要が生じたときに実施します。

1. Verifier と Agent は、Verifier がユーザーによる認可の証明を求める段階までやり取りします。
2. Verifier は操作の認可を示す Mandate の提示を要求します。
3. Agent は適切な Mandate を選んで提示します。Mandate がオープンな場合、Mandate が認めた鍵を使って取引に結び付けます。
4. Verifier は Mandate の完全性と、Mandate の内容が Agent の実行しようとする操作を許可していることを検証します。

選択的開示がある場合、Agent は認可を示すために必要な情報を提示しつつ、ユーザーのプライバシーを最大限に守れる開示内容を選ばなければなりません。適切な Mandate の選択方法は Shopping Agent の実装に依存し、この仕様の対象外です。

Verifier は Mandate を検証します（[検証と処理の規則](#verification-and-processing-rules) を参照してください）。Mandate を受理または拒否したとき、Verifier は署名付き Mandate Receipt を返さなければなりません。

成功を示す Mandate Receipt を受け取った Agent は、オープンな Mandate、クローズドな Mandate、Mandate Receipt の組を保存します。Receipt に基づいてオープンな Mandate の適用範囲を狭め、多くの場合は再提示できないようにします。

Mandate Receipt は Verifier 署名付き JWT で、次のプロパティを持ちます。

- `iss`：必須です。JWT の発行者を示す文字列で、Verifier でなければなりません。
- `result`：必須です。アクション認可の結果を表す `success` または `error` の列挙値です。
- `reference`：必須です。受信した Mandate のハッシュを base64url エンコードした文字列です。Mandate の連鎖を受け取った場合は、連鎖の最後の SD-JWT のハッシュです。`sd_hash` と同じ方法で計算します。使用するアルゴリズムは SD-JWT の `_sd_alg` と同じでなければならず、指定がない場合は `sha-256` を使います。
- `error`：任意です。エラーコードを示す文字列です。`result` が `error` の場合は必須です。
- `error_description`：任意です。人が読めるエラー説明です。

認可した操作や受け取った Mandate の型に応じた追加プロパティも含められます。

### エラー

すべてのアクション認可で次のエラーを使います。

- `invalid_credential`：Mandate の検証に失敗した場合に返します。終端エラーです。
- `unresolved_constraint`：Mandate に未知の制約がある場合、またはクローズドな Mandate が制約に適合するか検証できない場合に返します。直接承認されたクローズドな Mandate、または別の非エージェント型フローへの切り替えを促すために使えます。
- `invalid_mandate`：提示された Mandate が要求された操作を承認していない場合に返します。終端エラーです。
- `mandates_not_supported`：Verifier がこの操作の承認に Mandate を使えない場合に返します。非エージェント型フローへの切り替えを促すために使えます。

## 参考文献 { #references }

### 規範的文献

- [OpenID4VP] T. Lodderstedt、K. Yasuda、T. Looker「[OpenID for Verifiable Presentations](https://openid.net/specs/openid4vp-1_0.html)」、OpenID Foundation、2024年。
- [SD-JWT] D. Fett、B. Campbell、K. Yasuda、M. B. Jones「[Selective Disclosure for JWTs（SD-JWT）](https://datatracker.ietf.org/doc/rfc9901/)」、2025年2月。
- [Delegate SD-JWT] G. Oliver「[Delegate SD-JWT（個人草案）](https://github.com/GarethCOliver/gco-delegate-sd-jwt)」、2026年。
- [RFC7800] M. B. Jones、J. Bradley、H. Tschofenig「[Proof-of-Possession Key Semantics for JSON Web Tokens（JWTs）](https://datatracker.ietf.org/doc/html/rfc7800)」、2016年4月。

### 参考情報

- [OpenID4VCI] T. Lodderstedt、K. Yasuda、T. Looker「[OpenID for Verifiable Credential Issuance](https://openid.net/specs/openid4vc-issuance-1_0.html)」、OpenID Foundation、2024年。
- [ISO18013-5] ISO/IEC JTC 1/SC 17「[ISO/IEC 18013-5:2021 Personal identification — ISO-compliant driving licence — Part 5: Mobile driving licence (mDL) application](https://www.iso.org/standard/69084.html)」、2021年9月。
- [ISO18013-7] ISO/IEC JTC 1/SC 17「[ISO/IEC 18013-7:2024 Personal identification — ISO-compliant driving licence — Part 7: Mobile driving licence (mDL) add-on functions](https://www.iso.org/standard/82763.html)」、2024年10月。
