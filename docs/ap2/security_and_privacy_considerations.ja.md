# セキュリティとプライバシーに関する考慮事項

> このページは AP2 ドキュメントの非公式日本語訳です。
> [英語の原文を読む](https://github.com/google-agentic-commerce/AP2/blob/main/docs/ap2/security_and_privacy_considerations.md)

## セキュリティ上の考慮事項

エージェントコマースには多くのセキュリティリスクがあります。現在のエージェントセキュリティの状況を踏まえ、AP2 はプロンプトインジェクション攻撃の防止は困難だと想定します。そのため、すべての LLM とエージェントを潜在的な攻撃者として脅威モデルに含めます。

### 改ざんされたチェックアウト

**脅威：**

- 攻撃者が署名済みで承認済みの Payment Mandate を盗み、無関係な Checkout に使用します。

**対策：**

- Payment Mandate に、対応する Checkout への参照を含めます。
- クローズドな Payment Mandate では `transaction_id`、オープンな Payment Mandate では `mandate.payment.reference` 制約を使います。

**脅威：**

- 攻撃者がオープンな Payment Mandate を別のクローズドな Payment Mandate と組み合わせて再利用します。
- 攻撃者がオープンな Payment Mandate を使い、別のクローズドな Checkout Mandate を承認させます。

**対策：**

- クローズドな Mandate に `sd_hash` クレームを含め、提示されたオープンな Mandate に結び付けます。
- オープンな Mandate に `cnf` クレームで Agent の鍵を含めます。有効な署名を持つクローズドな Mandate を作成できるのは、そのエージェントだけになります。

**脅威：**

- 攻撃者がクローズドな Mandate を別のオープンな Mandate と組み合わせます。

**対策：**

- クローズドな Mandate に `sd_hash` クレームを含め、提示されたオープンな Mandate に結び付けます。

**脅威：**

- 攻撃者がクローズドな Checkout Mandate を別のチェックアウトセッションで使用します。

**対策：**

- 販売者は `checkout_hash` が最新の `checkout_jwt` のハッシュと一致することを検証します。

### 改ざんされた支払い

**脅威：**

- Shopping Agent または Credential Provider のエージェントが支払い内容を通信中に改ざんするか、ユーザーが承認した Mandate がない、または内容が異なる支払いを要求します。その結果、Credential Provider が Trusted Surface で承認されていない支払いを実行します。

**対策：**

- Merchant Payment Processor と Credential Provider は Payment Mandate のユーザー署名を検証し、完全性を確認します。
- `transaction_id` に含まれる `checkout_hash` で、支払いを対応する Checkout Mandate に安全に結び付けます。
- 制約を評価し、支払い金額と受取人が承認範囲内であることを確認します。

### 支払い資格情報の窃取

**脅威：**

- 攻撃者がユーザーの Payment Credential またはトークンを受け取り後に盗み、許可されていない状況で支払いに使います。

**対策：**

- 最終的な Payment Mandate を受け取り検証した後に限り、Payment Credential またはトークンを販売者に渡します。これによりトークンを特定の取引に結び付けます。

### 商品探索の改ざん

**脅威：**

- プロンプトインジェクションにより、Shopping Agent が悪意ある商品を選択したり、不適切な購入判断をしたりします。

**対策：**

- 販売者の署名で商品の提示内容の完全性を確認します。
- LLM が最適な選択をできなかった場合でも、クローズドな Mandate の検証時に制約を適用することで、金銭面と論理面の影響を許容範囲内に制限します。

### 二重支払い

**脅威：**

- プロンプトインジェクションなどで悪意を持った Shopping Agent が、同じオープンな Mandate を使って複数の有効な Checkout を承認します。

**対策：**

- Shopping Agent の非決定論的な処理部分は、先に提示した Mandate が拒否されたことを示す Receipt を受け取るまで、同じオープンな Mandate に対して対象範囲が重複するクローズドな Mandate に複数署名しないでください。
  - これらの Receipt は Shopping Agent の LLM から改ざんされないよう完全性を保護します。
- Credential Provider、決済ネットワーク、MPP は、対象範囲が重複する Mandate を拒否したり、発行済みの支払いトークンを無効化したりできます。

## プライバシー上の考慮事項

### オープンな Checkout Mandate と Payment Mandate の制約

オープンな Checkout Mandate と Payment Mandate の制約には、特定の Checkout には関係しない情報が含まれる場合があります。これを開示するとユーザーの意図が不必要に漏れる可能性があります。プライバシーを守るため、選択的開示を使います。

Trusted Surface は、プライバシーを高めるために RFC 9901 の 4.2.5 節にあるデコイダイジェストを挿入できます。

### Checkout と支払いのデータ最小化

ユーザーのプライバシーとデータ最小化の原則を守るため、選択的開示を使い、Checkout Mandate と Payment Mandate をそれぞれチェックアウトと支払いの保護に必要な関係者に共有します。`checkout_hash` で両 Mandate を関連付け、紛争時に照合できるようにします。

> 注：適切な合意や経路があれば、Mandate に含まれる情報や Mandate 自体を他の関係者と共有する場合がありますが、その方法は AP2 の対象外です。

### レインボーテーブル攻撃

Payment Mandate、Checkout Mandate、および制約に関する SD-JWT のダイジェストには、平文を推測されないよう十分なエントロピーを持つソルトを含めます。詳しくは RFC 9901 の 9.1 節を参照してください。

`checkout_hash` では JWT 署名に含まれるエントロピーを使い、Checkout の内容を推測しにくくします。`Ed25519` のような決定論的署名方式など、署名にそのエントロピーが含まれない方式を使う場合、Checkout に十分なエントロピーを持つソルトを含めます。
