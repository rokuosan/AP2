---
hide:
    - toc
---

<!-- markdownlint-disable MD041 -->
<div style="text-align: center;" markdown="1">
  <div class="centered-logo-text-group" markdown="span">
    ![Agent Payments Protocol のロゴ](assets/ap2-logo-black.svg){ width="100" }
    <h1>Agent Payments Protocol (AP2)</h1>
  </div>
</div>

> このページは AP2 ドキュメントの非公式日本語訳です。
> [英語の原文を読む](https://github.com/google-agentic-commerce/AP2/blob/main/docs/index.md)

## AP2 とは { #what-is-ap2 }

**Agent Payments Protocol（AP2）**は、エージェントが関わる経済活動のためのオープンなプロトコルです。
開発者、販売者、決済事業者が、安全で信頼性が高く、相互運用可能なエージェントコマースを実現できるように設計されています。
オープンソースの [Agent2Agent（A2A）プロトコル](https://a2a-protocol.org/)と [Universal Commerce Protocol（UCP）](https://ucp.dev/documentation/ucp-and-ap2/)の拡張として利用でき、ほかの連携も進んでいます。

<!-- prettier-ignore-start -->
!!! abstract ""

    **[![ADK のロゴ](https://google.github.io/adk-docs/assets/agent-development-kit.png){class="twemoji lg middle"} ADK](https://google.github.io/adk-docs/)** などのフレームワークでエージェントを作り、
    **[![MCP のロゴ](https://modelcontextprotocol.io/mcp.png){class="twemoji lg middle"} MCP](https://modelcontextprotocol.io)** などでツールに接続し、
    **[![A2A のロゴ](https://a2a-protocol.org/latest/assets/a2a-logo-black.svg){class="twemoji sm middle"} A2A](https://a2a-protocol.org)** で協調させます。
    **![AP2 のロゴ](./assets/ap2-logo-black.svg){class="twemoji sm middle"} AP2** を使えば、生成 AI エージェントで安全に支払いができます。
<!-- prettier-ignore-end -->

<div class="grid cards" markdown>

- :material-play-circle:{ .lg .middle } **動画** 7 分未満でわかる AP2

    ---

      <iframe width="560" height="315" src="https://www.youtube.com/embed/jSHj0z9Gi24?si=jDx8luqpw35nbDKy" title="AP2 の紹介動画（YouTube）" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

- :material-file-document-outline:{ .lg .middle } **ドキュメント**

    ---

    [:octicons-arrow-right-24: AP2 v0.2 の公開と FIDO Alliance への寄贈](https://blog.google/products-and-platforms/platforms/google-pay/agent-payments-protocol-fido-alliance/)

    [:octicons-arrow-right-24: FIDO Alliance が信頼できる AI エージェント間のやり取りに向けた標準を策定](https://fidoalliance.org/fido-alliance-to-develop-standards-for-trusted-ai-agent-interactions/)

    [:octicons-arrow-right-24: Agent Payments Protocol の発表（2025 年 9 月 16 日）](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)

    &nbsp;

    **AP2 の技術仕様と連携方法**

    [:octicons-arrow-right-24: Agent Payments Protocol 仕様](ap2/specification.md)

    [:octicons-arrow-right-24: AP2 と UCP の連携ガイド](https://ucp.dev/documentation/ucp-and-ap2/)

</div>

---

## Agent Payments Protocol が必要な理由 { #why-an-agent-payments-protocol-is-needed }

現在の決済システムは、利用者本人が信頼できるウェブサイトで購入ボタンを押すことを前提としています。
自律的なエージェントが支払いを開始すると、この前提が崩れ、既存のシステムでは答えにくい問題が生じます。

- **認可**：ユーザーが特定の購入を行う権限をエージェントに与えたことを、どう検証できるでしょうか。
- **真正性**：販売者は、エージェントの要求に誤りやハルシネーションがなく、ユーザー本人の意思を正確に反映していることを、どう確認できるでしょうか。
- **責任の所在**：不正な取引や誤った取引が起きたとき、ユーザー、エージェントの開発者、販売者、Issuer、決済サービス事業者（PSP）、オーケストレーション層のうち、誰が責任を負うのでしょうか。

こうした曖昧さは取引への信頼を損ない、普及を大きく妨げるおそれがあります。
共通のプロトコルがなければ、独自の決済システムが乱立し、ユーザーは使い分けに迷い、販売者は対応コストを負担し、金融機関の管理も複雑になります。
AP2 は、世界中で、プロトコルに準拠するエージェントと販売者が安全に取引するための共通の仕組みを提供することを目指しています。

---

## 設計原則と目標 { #core-principles-and-goals }

Agent Payments Protocol は、安全で公正なエコシステムを実現するため、次の原則に基づいています。

- **オープン性と相互運用性**：AP2 は、A2A や MCP 向けの非独占的なオープン拡張です。
  開発者が新しい機能を競って開発でき、販売者は幅広い利用者にアクセスでき、利用者はサービスを選択できます。
- **ユーザーの主導権とプライバシー**：最終的な主導権は常にユーザーが持ちます。
  プロトコルは参加者の役割を分け、機密性の高い支払い情報や個人情報を保護します。
- **検証可能な意思**：決済の信頼性を支えるのは、ユーザーの意思を示す確定的で否認できない証拠です。
  エージェントの誤りやハルシネーションによるリスクを抑えます。
- **明確な責任の所在**：AP2 は取引ごとに、否認できない暗号学的な監査証跡を提供します。
  これにより、紛争の解決を支援し、取引に関わる参加者が取引を信頼できるようにします。
- **世界各地の決済方式に対応できる設計**：初期バージョンでは、クレジットカードやデビットカードなど、一般的なプル型決済に対応します。
  即時決済を行える銀行システムがない国も多いことを踏まえ、今後は電子ウォレット、UPI や PIX といった即時銀行送金などのプッシュ型決済、デジタル通貨への対応を計画しています。

---

## Verifiable Digital Credential（VDC） { #key-concept-verifiable-digital-credentials-vdcs }

Agent Payments Protocol では、**Verifiable Digital Credential（VDC、検証可能なデジタル資格情報）**を使って取引を検証できるようにします。
VDC は、暗号学的に署名され、改ざんを検知できるデジタルオブジェクトであり、取引を構成する要素です。
主な Mandate は 2 種類あり、それぞれ Open と Closed の段階があります。

- **Checkout Mandate**：エージェントと販売者が取り決めた具体的な商品や購入内容への参照を記録し、**販売者に共有**します。
    - **Open**：エージェントが自律的に購入できるよう、カートが確定する前にユーザーが指定した取引の目的や制約を記録します。
    - **Closed**：確定した特定のチェックアウトについて、ユーザーまたはエージェントが与えた認可を記録します。
- **Payment Mandate**：特定の支払い手段による支払いを認可し、**Credential Provider、決済ネットワーク、Merchant Payment Processor に共有**します。
    - **Open**：エージェントが自律的に支払う際のユーザーの制約を記録します。
      制約には予算や利用できる支払い手段などがあります。
    - **Closed**：確定したチェックアウトに結び付けて、特定の取引金額に対する認可を記録します。

これらの VDC は、役割を定めたアーキテクチャの中で連鎖します。
これにより、ユーザーの参加の有無にかかわらず、取引全体を検証できる監査証跡が得られます。

具体例は[フロー](ap2/flows.md)を参照してください。

## サンプルで試す { #see-it-in-action }

<div class="grid cards" markdown>

- **ユーザー不在時のカード決済**

    ---

    エージェントがユーザーの不在時に、従来のカード決済を使って自律的に取引するサンプルです。

    [:octicons-arrow-right-24: サンプルを見る](https://github.com/google-agentic-commerce/AP2/tree/main/code/samples/python/scenarios/a2a/human-not-present/cards/)

- **ユーザー不在時の x402 決済**

    ---

    エージェントがユーザーの不在時に、x402 プロトコルを使って自律的に取引するサンプルです。

    [:octicons-arrow-right-24: サンプルを見る](https://github.com/google-agentic-commerce/AP2/tree/main/code/samples/python/scenarios/a2a/human-not-present/x402/)

- **Android の Digital Payment Credentials**

    ---

    Android デバイスで Digital Payment Credentials を使うサンプルです。

    [:octicons-arrow-right-24: サンプルを見る](https://github.com/google-agentic-commerce/AP2/tree/main/code/samples/android/scenarios/digital-payment-credentials/)

- **ユーザー参加時のカード決済**

    ---

    ユーザーが参加する取引で、従来のカード決済を使うサンプルです。

    [:octicons-arrow-right-24: サンプルを見る](https://github.com/google-agentic-commerce/AP2/tree/main/code/samples/python/scenarios/a2a/human-present/cards/)

</div>

---

## AP2 を試す方法と開発への参加 { #get-started-and-build-with-us }

Agent Payments Protocol は、エージェントを活用した商取引を広げる取り組みの一部として、安全に支払うための仕組みを提供します。
今後の商取引の仕組みをともに作るため、フィードバックやコントリビューションを歓迎します。

公開 GitHub リポジトリでは、AP2 の最新仕様、ドキュメント、SDK を提供しています。
仕様の標準化は、FIDO の Agentic Authentication Technical Working Group と Payments Technical Working Group で続けられます。

- **サンプルコード**をダウンロードして実行する。
- **プロトコルを試し**、エージェントのさまざまな役割を確認する。
- 公開リポジトリでフィードバックを伝え、**コード**を提供する。

[GitHub リポジトリを見る](https://github.com/google-agentic-commerce/AP2)
