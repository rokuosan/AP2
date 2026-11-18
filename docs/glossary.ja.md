# 用語集 { #glossary }

> このページは AP2 ドキュメントの非公式日本語訳です。
> [英語の原文を読む](https://github.com/google-agentic-commerce/AP2/blob/main/docs/glossary.md)

| 用語 | 略称 | 定義 | 同義語・関連語 |
| :--- | :--- | :--- | :--- |
| Action Authorization | | Verifier が Agent に、User に代わって特定のアクションを実行する権限の証明を求める手続き。 | |
| Agent Payments Protocol | AP2 | AI エージェントが安全に相互運用し、自律的に支払いを完了できるようにするオープンなプロトコル。 | |
| Agent Provider | | User に Agent を提供する主体。Verifier が Mandate を直接作成する際に信頼する相手にもなり得る。 | |
| Agent2Agent Protocol | [A2A](https://a2a-protocol.org/latest/) | 基盤となるフレームワークに関係なく、さまざまな AI エージェントが安全に通信し、協調してタスクを管理するためのオープン標準。<br><br>**AP2 との関係**：AP2 は A2A の拡張として実装でき、エージェントが関与する支払いの信頼性を確保しながら金銭取引を行えるようにする。 | |
| Agentic payments | | 自律的な AI エージェントが支払いを仲介するフロー。 | |
| Checkout Mandate | | チェックアウトの完了を認可するための Mandate。 | |
| Closed Mandate | | Verifier が関わる特定のアクションに結び付けられ、そのアクションを実行する権限を Agent に与える Mandate。 | |
| Credentials Provider | CP | デジタルウォレットのように、ユーザーの支払い資格情報と本人確認用の資格情報を安全に管理し、利用する主体。 | |
| Deterministic cryptographical proof | | ハードウェアデバイスに結び付けられる場合がある、一意な数学的証明。 | |
| Dynamic Linking | | Strong Customer Authentication（SCA）の主要な要件。特定の取引の詳細を Payment Credential に含め、SCA をその取引に結び付ける。<br><br>**用途**：金額や Payee などの取引の詳細に対し、Payer が明示的に同意したことを保証する。 | |
| Mandate Content | | Shopping Agent が作成して User に提示する Mandate の具体的なペイロード。Agent が実行するアクションの詳細を含む。 | |
| Mandate Delegation | | User が、自分に代わってアクションを実行する権限を Agent に与える手続き。 | |
| Mandate Receipt | | Action Authorization の結果を示す、Verifier が署名した JWT。 | |
| Merchant Endpoint (Or Remote Endpoint) | ME, RE | 販売者を代表し、商品を提示してカートの内容を交渉するウェブインターフェースまたは AI エージェント。 | |
| Merchant Payment Processor | MPP | 取引のオーソリゼーション要求を作成し、決済エコシステムに送信する主体。 | Merchant PSP |
| Model Context Protocol | MCP | AI モデルやエージェントがツール、API、データソースなどの外部リソースに接続し、操作する方法を標準化するプロトコル。 | |
| Open Mandate | | 特定のアクションにまだ結び付いていない Mandate。有効な Closed Mandate を作成する際に適用する制約を含む。 | |
| Payee | | 支払い取引で資金の受取先に指定された個人または組織。<br><br>**用途**：支払い確認と併せて証明書の提示を求めることができる。 | Merchant, Creditor Name |
| Payer | | 支払い口座を保有し、その口座からの支払い指図を認める個人または組織。<br><br>**用途**：支払い指図を開始する。 | User, Holder |
| Payment Agent | | エージェント決済で、最適な支払い方法の選択、支払い情報の検証、エラー処理を担う役割として提案されているエージェント。<br><br>**実装上の補足**：プロトコルへの参加に Payment Agent は必須ではない。MCP ベースのエンドポイントも同様の役割を担える。 | |
| Payment Credential | | 支払いの請求に使用できる資格情報、支払い手段、またはそれらへの参照。 | Electronic Attestation of Attributes (EAA), Payment Wallet Attestation (PWA), Digital Payment Credentials (DPC), Payment Means Attestation, SPC Credential |
| Payment Initiation Service Provider | PISP | ユーザーに代わって支払いを開始するサービス事業者。 | |
| Payment Mandate | | 特定のチェックアウトに対する支払いを認可するための Mandate。 | |
| Strong Customer Authentication | SCA | 金融サービスでのオンライン本人確認や取引開始において、規制上求められる認証手続き。<br><br>**決済ルールとの関係**：Payments Rulebook の中核に位置し、取引の安全性と Dynamic Linking を確保する。 | Strong User Authentication, Integrated SCA |
| Trusted Surface | | 認可と同意を得るため、Mandate Content を User に提示する、エージェントを介さない安全なインターフェース。この手続きで Mandate が作成される。 | |
| Universal Commerce Protocol (UCP) | | Checkout Mandate と併用する際に、Checkout Object の標準を提供するプロトコル。 | |
| User | | タスクを開始し、支払いの権限を与える人。 | |
| User Agent a.k.a. Shopping Agent | UA, SA | ユーザーと直接やり取りし、要望を把握して購入を調整する AI インターフェース。 | |
| Verifiable digital credential | VDC | 真正性を検証できる、Issuer が署名した資格情報（Claim の集合）。<br><br>**用途**：通常は暗号鍵に結び付けて、Issuer、Holder、Verifier からなるモデルで使用する。 | Digital credential, Verifiable Credential |
| Verifiable Presentation | VP | Verifier の要求に応じて作成する、1 つ以上の VDC の提示データ。Holder とのバインディングを示す暗号学的証明を含む。<br><br>**用途**：Verifier は、Holder が自分を提示先として指定したことを確認できる。提示には Claim の一部だけを含めることもできる。 | |
