# 実装上の考慮事項

## 役割

各役割が担う処理と、決済エコシステムでの実装例を示します。

### 販売者

販売者は次の機能を実装します。

- Shopping Agent がコマースプロトコルを利用できるように、商品カタログとチェックアウトのエンドポイントを提供します。例として [Universal Commerce Protocol](https://ucp.dev/) があります。
- 署名付き Checkout JWT を生成します。
- [Checkout Mandate](checkout_mandate.md) を検証します。Merchant Payment Processor などの技術提供者に委任することもできます。
- Checkout Mandate のハッシュと Payment Mandate に紐付く `payment_token` を使い、Merchant Payment Processor とチェックアウトを完了します。販売者が Merchant Payment Processor の役割を兼ねることもできます。
- 適切な状態を含む署名付き [Checkout Receipt](checkout_mandate.md#checkout-receipt) を生成し、Shopping Agent に返します。

販売者の構成例を示します。

- UCP エンドポイントを持つ販売者。
- Shopping Agent と agent-to-agent（a2a）で通信し、UCP 経由で販売者のバックエンドと通信する Merchant Agent。
- 販売者と Merchant Payment Processor を兼ねる事業者。
- Checkout Mandate の検証を外部委託する販売者。この場合、販売者は検証のために Mandate を技術提供者へ渡し、検証に成功した場合に処理を続行します。

### Merchant Payment Processor

Merchant Payment Processor は次の機能を実装します。

- 販売者から支払いトークンを受け取ります。
- トークン内の [Payment Mandate](payment_mandate.md) を検証します。
- 署名付き [Payment Receipt](payment_mandate.md#payment-receipt) を生成し、Shopping Agent、Credential Provider、決済ネットワークが利用できるようにします。
- 支払いを処理または検証します。

### Shopping Agent

Shopping Agent は次の機能を実装します。

- エージェントによる買い物を通じてユーザーの意図を判断します。
- Credential Provider から支払い手段を選択します。
- Checkout Mandate と Payment Mandate の内容を作成します。
- Trusted Surface を通じて署名済みの Checkout Mandate と Payment Mandate を取得します。
- 支払いトークンを得るために [Payment Mandate](payment_mandate.md) を Credential Provider に提示します。この処理には、保存済み Mandate の選択、必要に応じた Agent 鍵との鍵結合、選択的開示によるデータ最小化、二重支払いの防止、Receipt の管理が含まれます。
- チェックアウトを完了するため、[Checkout Mandate](checkout_mandate.md) を販売者に提示します。この処理にも、Mandate の選択、必要に応じた鍵結合、選択的開示によるデータ最小化、二重支払いの防止、Receipt の管理が含まれます。
- Receipt を受け取り、成功とエラーを処理します。

### Credential Provider

Credential Provider は次の機能を実装します。

- Shopping Agent に支払い手段を提供します。
- [Payment Mandate](payment_mandate.md) を検証します。
- Payment Mandate を使って決済ネットワークから支払いトークンを取得するか、販売者への送金を開始します。
- 支払いトークンまたは資金参照番号を渡します。
- [Payment Receipt](payment_mandate.md#payment-receipt) を受け取り、保存します。

Credential Provider の実装例を示します。

- Shopping Agent が連携するユーザーのデジタルウォレットまたは決済ネットワーク。
- Shopping Agent が直接提供する支払い手段の保管場所。
- 販売者が提供する支払い手段の保管場所。

### Trusted Surface

Trusted Surface は、エンドユーザーから承認と同意を得るために、すべての関係者が信頼する UI です。次の処理を担います。

- Checkout Mandate と Payment Mandate の内容をユーザーに表示します。
- ユーザーの承認と同意を取得します。
- 署名付き Checkout Mandate と Payment Mandate を作成し、Shopping Agent に委任します。

この役割はさまざまな主体が担えます。たとえば、Shopping Agent アプリケーション内の決定論的な部分、独立したユーザーウォレットや発行者アプリケーション、モバイルプラットフォームやブラウザーなどの信頼されたユーザーエージェントがあります。

## エージェントの識別

AP2 は、エージェント自体が信頼できることを前提とせず、その動作を制約するよう設計されています。コマースプロトコルの実装時に、販売者や Trusted Surface が信頼済みエージェントだけを利用対象にすることもあります。その詳細はコマースプロトコル層で扱います。

## ハッシュ

ハッシュを計算するときは、すべての当事者が同じ表現を使う必要があります。通常は JSON 構造を base64url エンコードした表現を使います。紛争解決に備え、Mandate の SD-JWT と開示情報をコンパクトシリアライゼーション形式で保存します。これにより `sd_hash`、`checkout_hash`、Receipt の `reference` を計算できます。

一貫性を保つため、SD-JWT のダイジェストと `checkout_hash` には同じハッシュアルゴリズムを使います。

## Agent 鍵

自律フローでは Agent 鍵を使い、オープンな Mandate を個別の取引に結び付けて再利用を防ぎます。また、対象期間が重なるクローズドな Mandate の発行を防ぎ、二重支払いを抑止します。

実装方法の一つはツール呼び出しを使うことです。決定論的なコードで、署名前に作成中のクローズドな Mandate を検証します。この検証を Shopping Agent から技術提供者に委任することもできます。

## Mandate の管理

Mandate は長期間有効なため、Shopping Agent は有効な Mandate と、それを使うタスクを管理する仕組みを用意することが望まれます。有効期間を制限し、自律実行中もユーザーに通知することで、ユーザーが Shopping Agent を管理しやすくなります。

外部の Trusted Surface を使う場合、委任した Mandate の管理機能を用意する方法もありますが、この仕様の対象外です。
