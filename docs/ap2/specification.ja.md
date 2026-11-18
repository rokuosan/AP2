# Agentic Payment Protocol（AP2）v0.2

Agentic Payment Protocol（AP2）は、エージェントが実行する支払い取引を保護するプロトコルです。[Agent Authorization モデル](agent_authorization.md)を利用します。

この仕様では、AP2 の役割と検証責任、購入対象を保護する [Checkout Mandate](checkout_mandate.md) と Receipt、Checkout の支払いを保護する関連付けられた [Payment Mandate](payment_mandate.md) と Receipt、紛争時にこれらを証拠として使う方法を定めます。

AP2 はコマースプロトコル内のセキュリティ機能として動作します。商品カタログ API、チェックアウトの更新、各役割間の通信 API など、コマースプロトコルの詳細は AP2 の対象外です。AP2 は Universal Commerce Protocol（UCP）との互換性を明示的に考慮して設計され、UCP と統合できます。

[人が参加する（`direct`）フロー](flows.md)と[人が参加しない（`autonomous`）フロー](flows.md)の例を示します。

## 役割

AP2 では、処理と検証の責任が異なる5つの役割を定義します。

- **Shopping Agent（SA）**：商品を探索し、チェックアウトを作成して購入を実行する主体です。
- **Credential Provider（CP）**：購入に使う Payment Credential の提供元です。エージェントがその資格情報にアクセスする権限を検証し、利用範囲を適切に限定します。
- **Merchant（M、販売者）**：チェックアウトを提供し、完了させます。Shopping Agent が対象商品を購入する承認を得ていることを検証し、在庫、価格、販売者割引の完全性を担います。
- **Merchant Payment Processor（MPP）**：購入の支払いを処理します。Credential Provider が共有した Payment Credential が、この Checkout の支払いに承認されていることを検証します。
- **Trusted Surface（TS）**：ユーザーが意図を理解したうえで同意したことを確認し、ユーザー署名付き Mandate を作成する信頼された UI です。

1つの主体が複数、またはすべての役割を担うこともできます。その場合、その主体は担う各役割の責任をすべて負います。

役割は、自らの責任を常に別の当事者へ委任できます。

## エージェント型と非エージェント型

役割はエージェント型または非エージェント型に分類できます。通信を非決定論的な LLM が処理する役割をエージェント型とします。通信が真正性と正しさを検証する決定論的なコードで処理され、役割内の処理を LLM に委任していない場合、その役割は非エージェント型です。

Merchant、Merchant Payment Processor、Credential Provider は、エージェント型にも非エージェント型にもできます。Trusted Surface は非エージェント型でなければなりません。Shopping Agent はエージェント型を想定しています。

2つの非エージェント型の役割の間で通信する場合、完全性の確保には標準的な Web セキュリティで十分です。一方、どちらかがエージェント型なら、そのエージェント自体が潜在的な攻撃者です。そのため、安全な通信には改ざんを検出できる仕組みが必要です。

AP2 は少なくとも Shopping Agent がエージェント型であることを前提とします。Trusted Surface と非エージェント型の販売者のように、支払いのやり取りが2つの非エージェント型 UI の間で直接行われる場合は、既存の e コマースセキュリティモデルで十分です。

特定の役割に対する検証や処理に言及する場合、その役割がエージェント型かどうかにかかわらず、決定論的なコードで実行しなければなりません。

## Mandate

AP2 は Mandate を使ってエージェントに権限を付与します。一般的な仕組みは[Agent Authorization Framework](agent_authorization.md)を参照してください。

AP2 は Checkout Mandate と Payment Mandate の2種類を定義します。Shopping Agent はユーザーが依頼したタスクを判断した後、両 Mandate の内容を作成します。その具体的な方法はこの仕様の対象外です。

Shopping Agent は Trusted Surface を使って署名済みの Checkout Mandate と Payment Mandate を取得し、支払いの承認とチェックアウトの完了に利用します。

### Checkout Mandate

Checkout Mandate は、Shopping Agent が作成した Checkout を購入する権限があることを、販売者に暗号学的に証明します。Shopping Agent が提示し、販売者が検証します。

販売者は Checkout を含む販売者署名付き JWT を Shopping Agent に渡さなければなりません。クローズドな Checkout Mandate は暗号学的ハッシュでこの Checkout JWT に結び付けます。

販売者は Checkout Mandate を受理または拒否した後、Checkout Receipt を返さなければなりません。構造の詳細は[Checkout Mandate](checkout_mandate.md)を参照してください。

### Mandate のバージョン

各 AP2 Mandate 型は `vct` クレームでスキーマを識別します。`vct` 値にはスキーマのバージョン番号となる数値接尾辞が含まれます（例：`mandate.payment.1`、`mandate.checkout.open.1`）。実装は接尾辞を含む `vct` の文字列全体を正確に照合しなければなりません。互換性のないスキーマ改訂では新しい接尾辞（例：`.2`）を使い、新旧のバージョンを明確に区別します。

### Payment Mandate

Payment Mandate は、Shopping Agent が特定の Checkout の支払いを許可されていることを、Credential Provider、決済ネットワーク、Merchant Payment Processor に暗号学的に証明します。Shopping Agent が提示し、これらの役割が検証します。

Payment Mandate は Checkout JWT の暗号学的ハッシュで特定の Checkout に結び付けます。レインボーテーブル攻撃を防ぐため、Checkout JWT にはデジタル署名方式（例：ECDSA）を使い、Ed25519 のような決定論的署名方式は使ってはなりません。

Merchant Payment Processor が Payment Mandate を受理または拒否した後、署名付き Payment Receipt を Shopping Agent、Credential Provider、および必要に応じて決済ネットワークに返さなければなりません。詳細は[Payment Mandate](payment_mandate.md)を参照してください。

## モード

AP2 には2つのモードがあります。

- **人が参加する（直接）**：ユーザーがクローズドな Checkout を直接確認し、Checkout と支払いを明示的に承認します。
- **人が参加しない（自律）**：ユーザーは自身の意図を満たすクローズドな Checkout と支払いの条件を確認し、承認します。その後 Shopping Agent がオープンな Mandate を使って、ユーザーに代わってクローズドな Checkout と Payment Mandate を作成し、承認します。

検証者が受け取るのは、モードにかかわらず常にクローズドな Payment Mandate と Checkout Mandate です。違いは Mandate の検証方法にあります。

直接モードでは、User Credential または Agent Provider の信頼リストを使い、クローズドな Mandate の署名がユーザーからのものだと検証します。

自律モードでは、クローズドな Mandate に Agent 鍵で署名します。この鍵への信頼は、ユーザー署名付きオープン Mandate または Agent Provider の信頼リストによって確立します。検証者は Mandate の制約を使って Checkout と支払いがユーザーの意図に合うことを確認します。検証に関係する制約だけを検証者に共有します。

### 直接モード（人が参加）

Shopping Agent は販売者からクローズドな Checkout の Checkout JWT を受け取ると、Checkout Mandate と Payment Mandate の内容を作成し、ユーザーへの表示と署名のために Trusted Surface に渡します。

署名済み Mandate を受け取った Shopping Agent は Payment Mandate を Credential Provider（必要に応じて決済ネットワークも含む）に転送して検証を受けます。検証に成功すると、Shopping Agent は支払い資格情報を受け取ります。

Shopping Agent は支払い資格情報と Checkout Mandate を販売者に渡します。販売者は Checkout を自ら作成した内容と照合し、販売者起点の請求であれば Merchant Payment Processor に支払いを開始します。

支払い方法が販売者への送金を開始する方式の場合、販売者は代わりに送金の確認を受け取り、入金を確認します。

処理が完了すると Checkout Receipt が Shopping Agent に返されます。Payment Receipt は Shopping Agent、Credential Provider、該当する場合は決済ネットワークに返されます。

詳細な例は[人が参加するフロー](flows.md)を参照してください。ユーザーがクローズドな Checkout を承認するため、販売者と Trusted Surface が直接通信する従来型の e コマース手順に置き換えられる場合もあります。

### 自律モード（人が参加しない）

Shopping Agent が自律的に動作する場合、オープンな Checkout Mandate と Payment Mandate の内容を作成し、Trusted Surface に承認させます。これらには Agent の公開鍵を `cnf` クレームとして含めなければなりません。オープンな Mandate はまだ特定の取引に結び付いていないため、利用を Agent に限定する必要があります。Shopping Agent がタスクを完了できる最短の期間を `exp` クレームに設定することを推奨します。

適切な Checkout を作成した後、Shopping Agent は Trusted Surface での承認を受ける代わりに Agent 鍵で署名して Checkout を承認できます。その場合、直接モードと同様に、ユーザー署名付きオープン Mandate とエージェント署名付きクローズド Mandate の両方を検証者に提示しなければなりません。

同じオープン Mandate を使って異なる Checkout を複数承認することを防ぐため、Shopping Agent は前の Mandate が拒否されたことを示す Receipt を受け取るまで、後続のオープンな Payment Mandate または Checkout Mandate を提示してはなりません。

ユーザーのプライバシーを守るため、Shopping Agent はクローズドな Mandate の評価に必要なオープンな Mandate の開示情報だけを提示しなければなりません。

処理が完了すると Checkout Receipt が Shopping Agent に返されます。Payment Receipt は Shopping Agent、Credential Provider、該当する場合は決済ネットワークに返されます。詳細は[人が参加しないフロー](flows.md)を参照してください。

現行仕様では、Shopping Agent が Checkout に応じて適用する Mandate と開示情報を都度判断します。将来、コマースプロトコルに明示的なクエリ言語を導入すれば、実用的な相互運用性を高められます。

#### エージェント間の委任

このプロトコルを使い、ある Shopping Agent から別の Shopping Agent に Mandate を委任することも概念上は可能ですが、現行仕様の対象外です。

## 紛争時の証拠

紛争時には Checkout Mandate と Receipt、および Payment Mandate と Receipt を組み合わせ、取引内容を否認できない形で示せます。紛争解決の方法、保持期間、取得要件の詳細はこの仕様の対象外です。

Checkout Mandate と Receipt は Shopping Agent または販売者が提供できます。Payment Mandate と Receipt は Shopping Agent、Credential Provider、決済ネットワーク、Merchant Payment Processor が提供できます。検証規則は[紛争時の検証]()を参照してください。

Shopping Agent または販売者から Checkout Mandate を自動取得する仕組みは、エコシステムに大きな利便性をもたらします。具体的な方法は現行版の対象外ですが、Payment Mandate の `transaction_id` をキーとして取得を要求する方法が考えられます。

## 検証

Mandate を受け取った各役割は、以下の検証規則に従わなければなりません。役割は技術提供者に責任を委任することもできます。たとえば販売者が Payment Processor に検証を任せる場合、委任先はその役割に適用される検証規則に従います。

### 販売者

販売者はチェックアウトを完了する前に、Shopping Agent から適切な Checkout Mandate を受け取らなければなりません。次の手順で検証します。

- [検証と処理の規則](agent_authorization.md)に従って Checkout Mandate を処理し、検証します。
- 承認対象として送信された Checkout JWT のハッシュが `checkout_hash` クレームの値と一致することを確認します。
- オープンな Checkout Mandate が含まれる場合、各制約を評価してクローズドな Checkout がすべての制約を満たすことを確認します。

いずれかの手順に失敗した場合、適切なエラーメッセージを含む Checkout Receipt JWT を返さなければなりません。

### Credential Provider と決済ネットワーク

Credential Provider と該当する場合は決済ネットワークは、支払い資格情報を返す前に Shopping Agent から適切な Payment Mandate を受け取らなければなりません。次の手順で検証します。

- [検証と処理の規則](agent_authorization.md)に従って Payment Mandate を処理し、検証します。
- オープンな Payment Mandate が含まれる場合、クローズドな Payment Mandate がすべての制約を満たすことを確認します。

いずれかの手順に失敗した場合、適切なエラーを含む Payment Receipt JWT を Shopping Agent に返さなければなりません。

### Merchant Payment Processor

Merchant Payment Processor は取引を処理する前に、販売者から適切な Payment Credential を受け取らなければなりません。Payment Credential が Checkout に適切に限定されていることを検証します。たとえば、クローズドな Payment Mandate を Payment Credential に含める方法があります。

### 紛争時の検証

紛争時には Payment Mandate、Checkout Mandate、および各 Receipt の完全性を確認するため、次の手順に従います。

- 販売者の検証規則に従って Checkout Mandate を検証します。
- 含まれる `checkout_jwt` から `checkout_jwt` のハッシュを独立して計算します。
- Checkout Receipt の `reference` がクローズドな Checkout Mandate のハッシュと一致することを確認します。計算方法は `sd_hash` と同じです。
- Checkout Mandate の `checkout_hash` を使い、[Merchant Payment Processor](#merchant-payment-processor) の節に従って Payment Mandate を検証します。
- Payment Receipt の `reference` がクローズドな Payment Mandate のハッシュと一致することを確認します。計算方法は `sd_hash` と同じです。

すべての手順に成功すれば、Checkout Mandate と Payment Mandate の情報を、ユーザーおよび各役割が確認した内容の証拠として利用できます。

## 拡張ポイント

AP2 にはエージェントコマースの要件に対応するため、次の拡張ポイントがあります。

### Mandate の制約

制約の拡張ポイントは、複雑な自律処理に対応しながらエージェントの動作を制限するためのものです。新しい制約を定義するには、一意な `type`、選択的開示の対象フィールドを含むスキーマ、制約の評価アルゴリズムを指定しなければなりません。

### Checkout オブジェクト

AP2 は販売者署名付き Checkout JWT の内容に依存しません。論理構造を持つ Checkout Object との互換性を想定していますが、ほかの Checkout Object に適応する拡張点も備えています。新しいコマース手順への対応には、UCP がプロトコル内に持つ拡張点を使う方法を推奨します。

### 支払い手段

AP2 は特定の支払い手段に依存しません。Payment Instrument JSON オブジェクトに一意な `type` を定義すれば、新しい支払い手段を追加できます。必要に応じて、その `type` 固有のプロパティも定義できます。

### 検証可能なデジタル資格情報形式（VDC）

AP2 は Payment Mandate と Checkout Mandate の保護に `SD-JWT` を指定します。Agent Authorization に記載されている他の VDC で暗号学的に保護することもできます。
