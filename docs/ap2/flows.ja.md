# フローの例

AP2 のフローは「人が参加する場合」と「人が参加しない場合」の2種類です。

- **人が参加する場合**：ユーザーがクローズドな Checkout Mandate と Payment Mandate を直接承認します。
- **人が参加しない場合**：ユーザーがオープンな Checkout Mandate と Payment Mandate を承認し、エージェントが自律的にそれらを提示するとともに、エージェント署名付きのクローズドな Mandate を提示します。

人が参加しないフローで `unresolved_constraint` エラーが返された場合、販売者（または Credential Provider）はユーザーに承認を求めることで、人が参加するフローに切り替えられます。

以下は規範的要件ではなく、フローの例です。事前に必要な登録とユーザー資格情報の設定が済んでいるものとします。

## 人が参加する場合

これは `direct` フローです。ユーザーがその場でクローズドな Payment Mandate と Checkout Mandate を承認します。

<figure markdown="span">
  ![AP2 の人が参加するフロー全体図](../assets/ap2_hp_flow.svg){ style="width:800px" }
  <figcaption align="center">人が参加するフロー</figcaption>
</figure>

このフローは2段階で進みます。

**フェーズ1：買い物**

<figure markdown="span">
  ![人が参加する買い物フロー](../assets/ap2_hp_shopping.svg){ style="width:800px" }
  <figcaption align="center">人が参加する買い物フロー</figcaption>
</figure>

1. ユーザーが Shopping Agent に買い物を依頼します。
2. Shopping Agent は販売者と通信し、カートを作成します。
3. Shopping Agent がチェックアウトに進むと、販売者は署名付き Checkout を作成し、続行に必要な Mandate を要求します。
4. Shopping Agent は Credential Provider から利用可能な Instrument Options を取得し、その中から1つを選びます。

**フェーズ2：支払い**

<figure markdown="span">
  ![人が参加する支払いフロー](../assets/ap2_hp_payment.svg){ style="width:800px" }
  <figcaption align="center">人が参加する支払いフロー</figcaption>
</figure>

1. Shopping Agent は Payment Mandate と Checkout Mandate の内容を組み立て、Trusted Surface を通じてユーザーに承認を求めます。
   - User Credential モデルでは外部の Trusted Surface、Trusted Agent Provider モデルでは内部の Trusted Surface を利用できます。
2. Trusted Surface は Mandate の内容を表示し、生体認証などによるユーザー認証と同意を得ます。
3. Trusted Surface は `user_sk` で署名し、Payment Mandate と Checkout Mandate を作成します。
   - `checkout_jwt` のハッシュで2つの Mandate を恒久的に関連付けます。
   - Trusted Agent Provider モデルでは `user_sk` は Agent Provider の鍵です。
4. Trusted Surface は Mandate を Shopping Agent に返します。
5. Shopping Agent は Payment Mandate を Credential Provider に渡します。Credential Provider は検証後、支払いトークンを作成します。
   - この処理で Credential Provider は Payment Mandate を決済ネットワークと共有し、利用範囲を限定した購入資格情報（トークン）を受け取る場合があります。
6. Shopping Agent はトークンと Checkout Mandate を販売者に送ります。
7. 販売者は Checkout Mandate の完全性と内容を現在のカートと照合し、トークンと `checkout_jwt` のハッシュを使って支払いを開始します。
8. Merchant Payment Processor はトークンに含まれる Payment Mandate と `checkout_jwt` のハッシュとの結び付きを検証します。
9. MPP 署名付き Payment Receipt が Shopping Agent、Credential Provider、決済ネットワークに返されます。販売者署名付き Checkout Receipt は成功を示すため Shopping Agent に返されます。

## 人が参加しない場合

<figure markdown="span">
  ![人が参加しないフロー](../assets/ap2_hnp_flow.svg){ style="width:800px" }
  <figcaption align="center">人が参加しないフロー</figcaption>
</figure>

**フェーズ1：買い物**

このフローの買い物段階は2つに分かれます。最初にユーザーが Shopping Agent に買い物のタスクを設定し、次にエージェントがユーザーの介入なしでタスクを実行します。

<figure markdown="span">
  ![人が参加しない買い物フロー](../assets/ap2_hnp_shopping.svg){ style="width:800px" }
  <figcaption align="center">人が参加しない買い物フロー</figcaption>
</figure>

**フェーズ1a：買い物（人が参加）**

ユーザーはオープンな Checkout Mandate と Payment Mandate を使って、自律的な購入をエージェントに許可します。

1. ユーザーが Shopping Agent に買い物を依頼します。
2. Shopping Agent は買い物セッションに適したオープンな Mandate の内容を組み立て、Trusted Surface を通じてユーザーに承認を求めます。
   - これにより、Shopping Agent が追加のユーザー承認なしで実行できる範囲を制約として定めます。
3. Trusted Surface は Mandate の内容を表示し、生体認証などによるユーザー認証と同意を得ます。
4. Trusted Surface は `user_sk` で署名し、オープンな Checkout Mandate と Payment Mandate を作成します。
   - オープンな Checkout Mandate のハッシュをオープンな Payment Mandate に含め、両者を恒久的に関連付けます。
   - Mandate の利用をエージェントに限定するため、確認クレームとして `agent_pk` を含めます。
   - Trusted Agent Provider モデルでは `user_sk` は Agent Provider の鍵です。

ユーザーはセッションを離れ、その後 Shopping Agent がタスクを自律的に実行します。

**フェーズ1b：買い物（人が不在）**

エージェントは割り当てられたタスクを満たすと判断した Checkout を作成します。

1. Shopping Agent は販売者と通信し、カートを作成します。
2. Shopping Agent がチェックアウトに進むと、販売者は署名付き Checkout を作成し、続行に必要な Mandate を要求します。

**フェーズ2：支払い（人が不在）**

エージェントはユーザーが事前に許可した Mandate を使ってチェックアウトを完了します。

<figure markdown="span">
  ![人が参加しない支払いフロー](../assets/ap2_hnp_payment.svg){ style="width:800px" }
  <figcaption align="center">人が参加しない支払いフロー</figcaption>
</figure>

1. Shopping Agent は、受け取った Checkout に適用できるオープンな Mandate を選びます。
   - Mandate の選択方法はこの仕様の対象外です。
   - 二重支払いを防ぐため、エラーを示す Action Receipt を受け取るまでは、Shopping Agent は重複する範囲の Mandate を複数作成してはなりません。詳しくは Implementation Considerations を参照してください。
2. Shopping Agent は Payment Mandate と Checkout Mandate の内容を組み立て、`agent_sk` で両方のクローズドな Mandate に署名します。
   - `checkout_jwt` のハッシュで両者を恒久的に関連付けます。
   - `kb-sd-jwt` の `sd_hash` プロパティでクローズドな Mandate をオープンな Mandate に結び付けます。
3. Shopping Agent はオープンおよびクローズドな Payment Mandate を Credential Provider に渡します。Credential Provider は検証後、支払いトークンを作成します。
   - この処理で Credential Provider は Payment Mandate を決済ネットワークと共有し、利用範囲を限定した購入資格情報（トークン）を受け取る場合があります。
4. Shopping Agent はトークンとオープンおよびクローズドな Checkout Mandate を販売者に送ります。
5. 販売者はクローズドな Checkout Mandate の完全性と内容を現在のカートと照合し、オープンな Checkout Mandate の制約が満たされていることを確認します。その後、トークン、`checkout_jwt` のハッシュ、オープンな Checkout Mandate のハッシュを使って支払いを開始します。
6. Merchant Payment Processor はトークン内の Payment Mandate と、`checkout_jwt` およびオープンな Checkout Mandate のハッシュとの結び付きを検証します。
7. MPP 署名付き Payment Receipt が Shopping Agent、Credential Provider、決済ネットワークに返されます。販売者署名付き Checkout Receipt は成功を示すため Shopping Agent に返されます。
