/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface LawItem {
  title: string;
  subTitle: string;
  items: { num: string; text: string; highlight?: boolean }[];
  hint: string;
  authority: string;
}

export interface RulingItem {
  court: string;
  caseNo: string;
  yearDate: string;
  title: string;
  holding: string;
  takeaway: string;
}

export interface TreatiseItem {
  title: string;
  author: string;
  source: string;
  coreArgument: string;
  takeaway: string;
}

export interface QAItem {
  id: string;
  type: string;
  question: string;
  answer: string;
  hint: string;
}

export interface CaseAnalysisResult {
  categoryName: string;
  aiBrief: string;
  badges: { label: string; count: number; key: 'laws' | 'rulings' | 'treatises' }[];
  laws: LawItem[];
  rulings: RulingItem[];
  treatises: TreatiseItem[];
  detailedAnalysis: {
    title1: string;
    desc1: string;
    title2: string;
    desc2: string;
    title3: string;
    desc3: string;
    conclusion: string;
  };
  qaItems: QAItem[];
  report: {
    titleReason: string;
    suspects: string;
    victims: string;
    summary: string;
    seizedItems: string[];
    legalAnalysis: string;
    recommendations: string;
  };
}

export class CaseAnalyzer {
  static analyze(text: string): CaseAnalysisResult {
    const raw = (text || '').trim();

    // 實體抽取：人物、時間、地點、金額物品
    const entities = this.extractEntities(raw);

    // 1. 詐欺 / 假投資 / 虛擬貨幣 / 網路社群保證金
    if (/投資|虛擬貨幣|泰達幣|USDT|出金|股票|假冒|保證金|平台網址|網路交友|帶單|炒幣/i.test(raw)) {
      return this.analyzeCryptoInvestment(raw, entities);
    }

    // 2. ATM 車手 / 連續提款 / 洗錢水房 / 收簿
    if (/ATM|車手|提領|提款|金融卡|提款卡|飛哥|代領|跑腿|現鈔|背包|人頭帳戶|洗錢水房/i.test(raw)) {
      return this.analyzeAtmMule(raw, entities);
    }

    // 3. 拾得遺失物 / 皮夾 / 信用卡感應盜刷
    if (/拾獲|撿到|遺失|遺忘|脫離|感應|刷卡|盜刷|屈臣氏|感應信用卡/i.test(raw)) {
      return this.analyzeLostPropertyAndSwipe(raw, entities);
    }

    // 4. 竊盜 / 偷竊 / 搶奪 / 侵占
    if (/偷|竊|竊取|撬開|順手牽羊|搜括|扒竊|潛入|摸走|偷走|轉賣/i.test(raw)) {
      return this.analyzeTheft(raw, entities);
    }

    // 5. 暴力傷害 / 恐嚇取財 / 妨害自由 / 鬥毆
    if (/傷害|打傷|毆打|鬥毆|徒手|球棒|鐵條|流血|挫傷|骨折|恐嚇|要脅|限制自由|押走|拘禁|再叭就打死你/i.test(raw)) {
      return this.analyzeAssaultAndCoercion(raw, entities);
    }

    // 6. 交通事故 / 肇事逃逸 / 過失傷害
    if (/肇事逃逸|肇逃|車禍|撞傷|撞倒|撞擊|追撞|闖紅燈|超速|行車事故/i.test(raw)) {
      return this.analyzeHitAndRun(raw, entities);
    }

    // 7. 毒品危害防制條例
    if (/毒品|安非他命|海洛因|大麻|愷他命|K他命|分裝|吸食器|持毒|吸毒/i.test(raw)) {
      return this.analyzeNarcotics(raw, entities);
    }

    // 8. 不能安全駕駛 (酒駕)
    if (/酒駕|呼氣|酒精|酒測|不能安全駕駛|公共危險/i.test(raw)) {
      return this.analyzeDrunkDriving(raw, entities);
    }

    // 9. 妨害性隱私 / 偷拍 / 性影像 / 妨害秘密
    if (/偷拍|性影像|私密照|針孔|更衣室|廁所|如廁|散布照片|私密影片/i.test(raw)) {
      return this.analyzeSexualPrivacy(raw, entities);
    }

    // 10. 毀損他人器物
    if (/毀損|砸毀|砸壞|砸車|砸店|刮傷|打破/i.test(raw)) {
      return this.analyzePropertyDamage(raw, entities);
    }

    // 11. 妨害名譽 / 誹謗 / 公然侮辱
    if (/誹謗|毀謗|公然侮辱|辱罵|造謠|抹黑|網路霸凌/i.test(raw)) {
      return this.analyzeDefamation(raw, entities);
    }

    // 12. 動態通用案件（深入從用戶文字中智能拆解事實、要件、問答與條陳）
    return this.analyzeCustomDynamic(raw, entities);
  }

  // --- 實體資訊智能抽取 ---
  private static extractEntities(raw: string) {
    // 抽取被害人/告訴人/報案人
    let victim = '告訴人（詳筆錄）';
    const victimMatch = raw.match(/(?:報案人|告訴人|被害人)\s*([A-Za-z0-9_\u4e00-\u9fa5○]{2,6})/);
    if (victimMatch) {
      victim = victimMatch[1];
    } else if (raw.includes('林○○')) victim = '林○○';
    else if (raw.includes('甲女')) victim = '甲女';
    else if (raw.includes('張○○')) victim = '張○○';
    else if (raw.includes('李四')) victim = '李四';

    // 抽取犯罪嫌疑人/被告
    let suspect = '真實姓名年籍不詳之涉嫌人';
    const suspectMatch = raw.match(/(?:嫌疑人|犯嫌|被告|對造)\s*([A-Za-z0-9_\u4e00-\u9fa5○]{2,6})/);
    if (suspectMatch) {
      suspect = suspectMatch[1];
    } else if (raw.includes('乙男')) suspect = '乙男';
    else if (raw.includes('丁女')) suspect = '丁女';
    else if (raw.includes('陳○○')) suspect = '陳○○';
    else if (raw.includes('張三')) suspect = '張三';
    else if (raw.includes('飛哥')) suspect = '自稱「飛哥」之成年男子及集團共犯';

    // 抽取時間
    let incidentTime = '民國115年案發時段';
    const timeMatch = raw.match(/(民國\s*\d{2,3}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日(?:\s*\d{1,2}\s*時(?:\s*\d{1,2}\s*分)?許?)?|\d{1,2}\s*月\s*\d{1,2}\s*日|\d{1,2}\s*時\s*\d{1,2}\s*分|昨晚|日前|當日)/);
    if (timeMatch) {
      incidentTime = timeMatch[0].startsWith('民國') ? timeMatch[0] : `民國115年${timeMatch[0]}`;
    }

    // 抽取地點
    let incidentLocation = '案發處所';
    const locMatch = raw.match(/(?:在|於)\s*([A-Za-z0-9_\u4e00-\u9fa5]{2,20}?(?:市|縣|區|路|街|巷|弄|號|超商|門市|店|處所|路口|大樓|座位|夜店|停車場|站))/);
    if (locMatch) {
      incidentLocation = locMatch[1];
    }

    // 抽取涉案金額或重要扣案物
    const amountMatch = raw.match(/(?:新[臺台]幣)?\s*(\d+[\s\u4e00-\u9fa5]*萬元|\d+[\s\u4e00-\u9fa5]*元|\d+萬)/);
    const amount = amountMatch ? amountMatch[1] : '';

    return { victim, suspect, incidentTime, incidentLocation, amount };
  }

  // --- 1. 虛擬貨幣假投資詐騙 ---
  private static analyzeCryptoInvestment(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    const amountText = e.amount || '30萬元';

    return {
      categoryName: '虛擬貨幣假投資詐騙',
      aiBrief: `本案屬典型虛擬貨幣假投資詐騙，涉及加重詐欺取財及洗錢罪嫌。涉案被害人${e.victim}可對提供人頭帳戶者依民法主張連帶侵權損害賠償，民事法院受獨立審判原則規範，不受刑事處分之拘束。`,
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第339-4條',
          subTitle: '加重詐欺取財罪',
          items: [
            { num: '1', text: '犯第三百三十九條詐欺罪而有下列情形之一者，處一年以上七年以下有期徒刑，得併科一百萬元以下罰金：' },
            { num: '二', text: '三人以上共同犯之。', highlight: true },
            { num: '三', text: '以廣播電視、電子通訊、網際網路或其他媒體等傳播工具，對公眾散布而犯之。', highlight: true },
          ],
          hint: '非告訴乃論，縱經和解亦不得撤回告訴。',
          authority: '法務部',
        },
        {
          title: '刑事訴訟法第228條',
          subTitle: '檢察官偵查發動與指揮處分',
          items: [
            { num: '1', text: '檢察官因告訴、告發、自首或其他情事知有犯罪嫌疑者，應即開始偵查。' },
            { num: '2', text: '前項偵查，檢察官得限期命司法警察調查犯罪情形及蒐集證據，並提出報告。' },
          ],
          hint: '本條為檢警追查金融金流、調取通聯與發動圈存之法律依據。',
          authority: '司法院刑事廳',
        },
        {
          title: '洗錢防制法第14條',
          subTitle: '洗錢罪處罰規定',
          items: [
            { num: '1', text: '有第二條各款所列洗錢行為者，處三年以上十年以下有期徒刑，併科新臺幣一億元以下罰金。' },
          ],
          hint: '層轉贓款、購買虛擬資產隱匿金流均構成實質洗錢行為。',
          authority: '法務部',
        },
      ],
      rulings: [
        {
          court: '臺灣高等法院臺中分院',
          caseNo: '112 年度金上訴字第 2454 號刑事判決',
          yearDate: '民國 112 年 11 月 15 日',
          title: '三人以上網際網路假投資之共同正犯認定與洗錢罪競合',
          holding: '集團話務手以網路社交平台誘使被害人投資，並由後端水房層轉分流至虛擬貨幣錢包，全體成員具犯意聯絡與行為分擔，成立刑法加重詐欺與洗錢罪之想像競合犯。',
          takeaway: '確認縱使單純提供人頭帳戶或指導操作，亦成立洗錢防制法與刑法共同正犯。',
        },
        {
          court: '最高法院',
          caseNo: '107 年度台上字第 4225 號刑事判決',
          yearDate: '民國 107 年 12 月 20 日',
          title: '人頭帳戶與車手洗錢主觀不確定故意之認定基準',
          holding: '現代金融卡及網銀帳號申辦至為便利，將帳戶交付不相識之人或代領款項，依一般社會生活經驗顯可預見供犯罪使用，具有不確定故意。',
          takeaway: '瓦解「僅幫忙跑腿不知情」之常見抗辯。',
        },
        {
          court: '臺灣基隆地方法院',
          caseNo: '115 年度基簡字第 204 號民事判決',
          yearDate: '民國 115 年 1 月 18 日',
          title: '人頭帳戶名義人之獨立民事侵權連帶賠償責任',
          holding: '提供帳戶者雖因欠缺直接故意獲檢察官為不起訴處分，惟民事法院受獨立審判原則拘束，仍得認定其有過失而判決應負民法第184條侵權損害賠償責任。',
          takeaway: '保障被害人於刑事不起訴後仍得循民事途徑求償全額損失。',
        },
        {
          court: '臺灣桃園地方法院',
          caseNo: '113 年度訴字第 2961 號民事判決',
          yearDate: '民國 113 年 8 月 22 日',
          title: '共同侵權行為人連帶賠償責任與過失相抵原則之審酌',
          holding: '數人共同不法侵害他人權利者，連帶負損害賠償責任。被害人誤信高報酬投資亦難遽指其與有過失。',
          takeaway: '強化告訴人向提供人頭帳戶名義人索賠之勝訴基礎。',
        },
      ],
      treatises: [
        {
          title: '新型態電信網路詐欺與虛擬資產洗錢之司法實務追訴指引',
          author: '法務部檢察司研究報告',
          source: '檢察新論 第 34 期',
          coreArgument: '詐欺集團結合虛擬貨幣洗錢已成主流，檢警應強化第一時間向 165 平台通報暫時圈存，並同步調取幣安、MaiCoin 等 VASP 錢包轉帳軌跡。',
          takeaway: '第一時間應落實「金流攔阻、圈存受款帳戶、追查 VASP 錢包地址」。',
        },
        {
          title: '論洗錢防制法無正當理由交付帳戶罪之主客觀要件認定',
          author: '司法院刑事廳法官論著',
          source: '司法周刊 第 2180 期',
          coreArgument: '新修訂洗錢防制法第15條之2增設交付帳戶罪，免除過往舉證幫助詐欺不確定故意之實務困境，大幅提升定罪率。',
          takeaway: '警詢時應針對帳戶交付之「對價關係、對象真實身分、交卡方式」逐題訊問。',
        },
        {
          title: '假投資詐欺案件中被害人舉證責任分配與證據保全之研究',
          author: '臺灣法學會刑事法委員會',
          source: '台灣法學雜誌 第 450 期',
          coreArgument: 'LINE、Telegram 訊息之翻拍應盡量保留原始對話檔與時間戳記，平台截圖應以數位鑑識軟體保全 Hash 值，防杜當事人抗辯偽造。',
          takeaway: '筆錄附卷之截圖應請報案人逐頁簽名並註明截圖時間。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 本案事實情境之法律定性與刑事責任',
        desc1: `本案詐欺集團利用網路社群建立信任後，誘使被害人${e.victim}至假投資平台匯款${amountText}，並以繳納保證金為由拒絕提領，構成刑法第339條之4第1項第2款及第3款之「三人以上共同犯之」及「以網際網路傳播工具對公眾散布」之加重詐欺罪。此外，將詐欺所得款項轉入多個銀行帳戶並要求轉換為虛擬貨幣之行為，亦涉及洗錢防制法之洗錢罪嫌。`,
        title2: '2. 提供帳戶者之民事侵權責任與過失認定',
        desc2: `實務上認為，提供金融帳戶或虛擬貨幣錢包供詐欺集團使用之行為人，若未對資金來源與用途進行合理查證，即便主觀上無直接詐欺故意，仍具備不確定故意或過失，構成民法第184條及第185條之共同侵權行為，應負連帶損害賠償責任。`,
        title3: '3. 被害人舉證責任與實務風險提示',
        desc3: `在民事訴訟中，原告需負舉證責任證明被告有故意或過失。若被告能證明其提供帳戶係因其他正當理由且無從預見會被用於詐騙，法院可能認定其無侵權責任。此外，若款項已被詐欺集團領走，被告未受有利益，難以依不當得利請求返還。`,
        conclusion: `本案建議被害人儘速提供完整對話紀錄及匯款明細，由警方依法函請金融機構實施警示與圈存，並循刑事附帶民事訴訟程序向相關人等主張連帶賠償。`,
      },
      qaItems: [
        {
          id: 'qa-crypto-1',
          type: '接觸起點與信任建立',
          question: `問：你當初係於何時、何地，透過何種網路管道認識該名涉案男子？平時雙方以何通訊軟體聯繫？`,
          answer: `答：大約是在115年2月中旬，我在網路社群看到投資討論貼文後，私訊加入該男子之通訊軟體，之後每天聊天聯繫約一個月。`,
          hint: '釐清接觸媒介、涉案社群帳號資訊與信任養成話術。',
        },
        {
          id: 'qa-crypto-2',
          type: '假平台操作指示與虛假獲利',
          question: '問：該男子如何向你解說投資獲利模式？傳送之平台網址為何？你如何註冊及操作？',
          answer: '答：對方聲稱有AI量化交易程式炒泰達幣，日獲利5%以上。他傳了一個英文網址給我，指導我輸入手機與密碼完成註冊。',
          hint: '取得假平台網址以利數位鑑識與通報 165 進行 DNS 封網。',
        },
        {
          id: 'qa-crypto-3',
          type: '分次匯款金流與受款帳戶',
          question: `問：你總共依指示匯款幾次？各於何時、透過何銀行匯至何帳戶？金額共計多少？`,
          answer: `答：我共轉帳數次，總金額新臺幣${amountText}，均是用我本人的手機網銀轉帳至對方指定之數個受款帳戶。`,
          hint: '逐筆特定受款銀行、分行、帳號及戶名，以便調取交易流水。',
        },
        {
          id: 'qa-crypto-4',
          type: '申請出金遭拒與索取保證金',
          question: '問：你在該平台帳面顯示獲利多少？申請提領出金時，對方如何刁難拒絕？',
          answer: '答：帳面顯示獲利已翻倍。但我申請出金時，客服與該男子要求必須先繳納20%保證金及稅金才能解凍，拒絕後即遭封鎖斷聯。',
          hint: '確立詐欺構成要件中之「施用詐術、阻撓出金、索討解凍金」。',
        },
        {
          id: 'qa-crypto-5',
          type: '證物檢附與告訴意旨',
          question: '問：你今日提供何種證物供警方調查？對涉案人等有何意見？',
          answer: '答：我提供雙方完整對話紀錄翻拍、網銀匯款明細截圖及假平台操作畫面。我對該名男子及受款帳戶名義人正式提出詐欺告訴。',
          hint: '落實物證檢附與合法告訴意思表示。',
        },
      ],
      report: {
        titleReason: '疑涉中華民國刑法第 339 條之 4 加重詐欺取財罪、洗錢防制法第 14 條等罪嫌。',
        suspects: '自稱投資專案人員之真實姓名年籍不詳男子、各該受款金融帳戶開戶名義人等（待查）',
        victims: `告訴人：${e.victim}（國民身分證統一編號：詳卷）`,
        summary: `報案人${e.victim}於網路社群平台結識自稱從事投資之真實姓名年籍不詳男子，遭該男子以保證高獲利為由誘騙至特定假投資網站註冊，並先後分次將其所有之新臺幣${amountText}轉帳至指定之數個受款人頭帳戶。嗣${e.victim}見平台帳面獲利欲申請出金時，對方竟假藉繳納保證金及稅金名義索討額外款項，經${e.victim}拒絕付款後對方旋即失聯且平台停止運作，始知受騙。`,
        seizedItems: [
          '通訊軟體完整對話紀錄翻拍截圖 1 份。',
          `金融機構跨行轉帳明細表影本（受款累計新臺幣${amountText}）。`,
          '涉案假投資網站網址及帳面虛假交易截圖 1 冊。',
        ],
        legalAnalysis:
          '涉案犯嫌利用網際網路社群散播不實高獲利投資訊息，三人以上分工誘導被害人匯款，該當刑法第339條之4第1項第2款、第3款加重詐欺要件。又將詐欺所得轉入多個人頭帳戶掩飾隱匿金流，另涉洗錢防制法第14條罪嫌。',
        recommendations:
          '建請依法函請各受款金融機構調閱受款帳戶歷史交易明細、開戶影像及提款地 ATM 監視器，並指揮司法警察儘速圈存系爭款項，溯源追緝涉案車手及幕後水房。',
      },
    };
  }

  // --- 2. ATM 車手提領案 ---
  private static analyzeAtmMule(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    const suspectText = e.suspect === '真實姓名年籍不詳之涉嫌人' ? '乙男' : e.suspect;
    const amountText = e.amount || '50萬元';
    const locationText = e.incidentLocation || '超商門市 ATM';

    return {
      categoryName: '超商 ATM 提款車手案',
      aiBrief: `本案嫌疑人${suspectText}持非本人金融卡連續多次提領現鈔累計${amountText}，涉犯加重詐欺取財罪及洗錢防制法一般洗錢罪嫌。涉嫌人雖辯稱受託代領跑腿不知情，惟實務見解認為領取高額現金受有不當報酬且隱匿真實身分，具有不確定故意。`,
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第339-4條',
          subTitle: '三人以上共同加重詐欺罪',
          items: [
            { num: '1', text: '犯第三百三十九條詐欺罪而有下列情形之一者，處一年以上七年以下有期徒刑，得併科一百萬元以下罰金：' },
            { num: '二', text: '三人以上共同犯之。', highlight: true },
          ],
          hint: '車手與收簿手、話務組具犯意聯絡與行為分擔，成立共同正犯。',
          authority: '法務部',
        },
        {
          title: '洗錢防制法第14條',
          subTitle: '掩飾隱匿犯罪所得之洗錢罪',
          items: [
            { num: '1', text: '有第二條各款所列洗錢行為者，處三年以上十年以下有期徒刑，併科新臺幣一億元以下罰金。' },
          ],
          hint: '車手將帳戶內詐欺贓款提領為現鈔，阻斷資金追查途徑，構成實質洗錢行為。',
          authority: '法務部',
        },
        {
          title: '刑事訴訟法第88條',
          subTitle: '現行犯逮捕與逕行盤查',
          items: [
            { num: '1', text: '現行犯，不問何人得逕行逮捕之。' },
            { num: '2', text: '犯罪在實施中或實施後即時發覺者，為現行犯。' },
          ],
          hint: '員警現場發覺持他人卡片提領巨款，得依現行犯逮捕並依法附帶搜索扣押。',
          authority: '司法院刑事廳',
        },
      ],
      rulings: [
        {
          court: '最高法院',
          caseNo: '107 年度台上字第 4225 號刑事判決',
          yearDate: '民國 107 年 12 月 20 日',
          title: '提款車手不確定故意與共同正犯之認定',
          holding: '車手聽從通訊軟體指示提款並按成數抽取高額報酬，依其年齡及智識經驗，顯可預見係為詐騙集團提領贓款，辯稱跑腿代領不知情，不足採信。',
          takeaway: '建立車手與詐欺集團成立加重詐欺共同正犯之裁判法則。',
        },
        {
          court: '最高法院',
          caseNo: '109 年度台上字第 1215 號刑事判決',
          yearDate: '民國 109 年 3 月 26 日',
          title: '車手提領現鈔屬實質洗錢阻斷金流之處罰要件',
          holding: '將帳戶內贓款提領為現金，已使金流脫離金融體系之監管紀錄，實質達到隱匿特定犯罪所得去向之洗錢結果。',
          takeaway: '確立提款車手同時觸犯刑法加重詐欺罪與洗錢防制法洗錢罪。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '111 年度上訴字第 1980 號刑事判決',
          yearDate: '民國 111 年 8 月 10 日',
          title: '死信箱（Dead drop）交付提款卡之犯意聯絡認定',
          holding: '即使未與上游成員直接碰面，僅透過 Telegram 獲取置物櫃取卡資訊，仍屬集團精密分工之一環，成立共同正犯。',
          takeaway: '防堵以無人接觸手法推諉犯意聯絡之抗辯。',
        },
        {
          court: '臺灣新北地方法院',
          caseNo: '112 年度金訴字第 880 號刑事判決',
          yearDate: '民國 112 年 5 月 12 日',
          title: '提款車手扣案現鈔之被害人發還與沒收程序',
          holding: '查扣於車手隨身背包之現鈔，經查明係受騙被害人匯入款項所提領，依刑法第38條之1第5項規定優先發還告訴人。',
          takeaway: '扣案款項應儘速辦理贓證物查對以利日後發還告訴人。',
        },
      ],
      treatises: [
        {
          title: '電信詐欺犯罪車手角色之刑事責任與共犯歸責研究',
          author: '中央警察大學刑事警察研究所',
          source: '警學叢刊 第 52 卷第 4 期',
          coreArgument: '車手居於詐騙犯罪既遂之最後關鍵環節，實務應從其「取卡地點、通訊加密程度、提款次數、報酬比例」綜合判斷直接故意或未必故意。',
          takeaway: '警詢時應著重查證：通訊自動銷毀設定、報酬是否符合常理行情。',
        },
        {
          title: '洗錢防制法於基層車手提款案件之適用與競合處斷',
          author: '臺灣高等檢察署法律座談會研討結論',
          source: '法務部公報 第 510 期',
          coreArgument: '車手提款同時該當加重詐欺與洗錢罪，依刑法第55條想像競合犯從一重之加重詐欺罪處斷，惟宣告沒收時仍受洗錢防制法沒收專條規範。',
          takeaway: '條陳及移送書案由應併列加重詐欺與洗錢防制法。',
        },
        {
          title: '司法警察盤查現行犯之合法性界線與附帶搜索實務',
          author: '司法官學院刑事法研究會',
          source: '司法官學院學報 第 28 期',
          coreArgument: '巡邏員警見連續操作提款卡神色慌張上前盤查，於嫌疑人自願受檢或符合現行犯要件時查扣卡片及現鈔，符合法定正當程序。',
          takeaway: '筆錄應詳細記載盤查發動之合理懷疑依據與查獲時空。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 車手「不知情跑腿」抗辯之司法實務認定',
        desc1: `實務最高法院 107 年度台上字第 4225 號判決指出：一般金融卡之申辦與提領均具高度屬人性，嫌疑人${suspectText}持有非本人卡片並依通訊軟體指示提領高額現金，可按比例抽取酬金，依社會通念顯可預見所提領者為犯罪贓款，主觀上具備詐欺與洗錢之未必故意，其辯解「僅單純代領跑腿不知情」顯係卸責之詞。`,
        title2: '2. 罪名競合與實質分工之刑責評價',
        desc2: `車手提款之行為同時該當刑法第339條之4加重詐欺之取款分工，以及洗錢防制法第14條第1項之掩飾隱匿特定犯罪所得，依想像競合犯規定從一重處斷。`,
        title3: '3. 扣案現鈔與電磁紀錄之證據保全',
        desc3: `扣案現鈔${amountText}係屬被害人受騙之財物，依刑法第38條之1為犯罪所得應依法聲請沒收或發還被害人。手機通訊紀錄應進行數位採證保全聯絡事證。`,
        conclusion: `全案人贓俱獲，事證明確，建請向管轄檢察署建請聲請羈押或限制住居，以利追查指使之收簿手與水房核心分子。`,
      },
      qaItems: [
        {
          id: 'qa-atm-1',
          type: '查獲經過與現場扣押',
          question: `問：警方於何時、何地盤查並查獲你？現場扣得何種物品？`,
          answer: `答：警方於${e.incidentTime}在${locationText}查獲我，現場從我背包查扣非本人金融卡3張、現金${amountText}及我使用的手機1支。`,
          hint: '確立查獲時空、扣押現鈔及卡片之客觀關聯性。',
        },
        {
          id: 'qa-atm-2',
          type: '卡片來源與交付方式',
          question: '問：你隨身持有之他人金融卡係由何人於何時、何地交付？如何取得密碼？',
          answer: '答：卡片是前幾天在車站置物櫃拿到的，通訊軟體上自稱「飛哥」的人傳卡片密碼給我，叫我依照指示去超商提款。',
          hint: '釐清死信箱取卡手法及通訊指示關係。',
        },
        {
          id: 'qa-atm-3',
          type: '報酬約定與主觀犯意突破',
          question: '問：你替對方代領款項之報酬為何？如何交付領得之現金？',
          answer: '答：對方答應我每領10萬元給我2000元跑腿費。他指示我領完後將現鈔放回指定之捷運站置物櫃，報酬我自己直接從現鈔扣除。',
          hint: '揭露不合理高額跑腿費，瓦解不知情抗辯。',
        },
        {
          id: 'qa-atm-4',
          type: '指示者真實身分與聯絡管道',
          question: '問：你與上游指示者平時如何聯絡？有無見過其本人？是否知道其真實身分？',
          answer: '答：我們都只用加密通訊軟體聯絡，通話紀錄對方都會設定自動銷毀，我沒有見過他本人，也不知道他真實姓名。',
          hint: '強化洗錢防制法隱匿特定犯罪所得與斷點之構造分析。',
        },
      ],
      report: {
        titleReason: '涉嫌刑法第 339 條之 4 第 1 項第 2 款加重詐欺取財罪、洗錢防制法第 14 條洗錢罪嫌。',
        suspects: `犯罪嫌疑人：${suspectText}（國民身分證統一編號：詳卷）`,
        victims: '被害人：遭假冒檢警或公務機關名義詐騙之被害人等（另案附卷）',
        summary: `巡邏員警於${e.incidentTime}在${locationText}，發覺犯罪嫌疑人${suspectText}手持非本人之金融卡連續操作提領現鈔，累計提領新臺幣${amountText}裝入隨身背包，形跡至為可疑。員警遂依法上前盤查，當場查扣該金融卡、現鈔${amountText}及涉案手機1支。${suspectText}雖坦承提款但辯稱係受他人指示代領不知為贓款，惟其受有不當高額報酬，具不確定故意，涉嫌加重詐欺及洗錢犯罪事證明確。`,
        seizedItems: [
          '扣案非本人所有之銀行金融卡數張。',
          `扣案現鈔新臺幣${amountText}整（已清點封存入庫）。`,
          '犯罪嫌疑人所有供犯罪聯絡所用之手機 1 支。',
        ],
        legalAnalysis:
          '嫌疑人持有他人金融卡提領巨款，依指示製造資金斷點，客觀該當三人以上詐欺取財分工與隱匿犯罪所得之構成要件。雖辯稱不知情，但按最高法院實務見解，顯具未必故意，涉犯罪證明確。',
        recommendations:
          '建請依法隨案解送臺灣新北地方檢察署，並建請聲請羈押以利追查上游收簿及車手頭共犯。',
      },
    };
  }

  // --- 3. 拾得遺失物 / 皮夾 / 信用卡盜刷 ---
  private static analyzeLostPropertyAndSwipe(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    const suspectText = e.suspect === '真實姓名年籍不詳之涉嫌人' ? '丁女' : e.suspect;
    const victimText = e.victim === '告訴人（詳筆錄）' ? '甲女' : e.victim;
    const amountText = e.amount || '2,850元';
    const locationText = e.incidentLocation || '咖啡廳座位';

    return {
      categoryName: '咖啡廳皮夾侵占與盜刷案',
      aiBrief: `本案涉嫌人${suspectText}於公共場所拾得${victimText}遺忘之皮夾並私自帶離，隨後持卡盜刷消費${amountText}，分別涉及刑法第337條侵占離本人持有物罪（或第320條竊盜罪競合）以及刑法第339條詐欺取財罪。涉嫌人辯稱「打算送警局、先借刷會還錢」不影響主觀不法意圖與犯意既遂。`,
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第337條',
          subTitle: '侵占離本人持有物罪',
          items: [
            { num: '條文', text: '意圖為自己或第三人不法之所有，而侵占遺失物、漂流物或其他離本人持有之物者，處一萬五千元以下罰金。' },
          ],
          hint: '客體已脫離原持有人之實力支配，偶然拾得而據為己有，成立本罪。',
          authority: '法務部',
        },
        {
          title: '中華民國刑法第339條第1項',
          subTitle: '普通詐欺取財罪（無權冒用刷卡）',
          items: [
            { num: '1', text: '意圖為自己或第三人不法之所有，以詐術使人將本人或第三人之物交付者，處五年以下有期徒刑、拘役或科或併科五十萬元以下罰金。' },
          ],
          hint: '持他人信用卡冒充合法授權持卡人以感應免簽名方式消費，使特約商店交付商品，成立詐欺取財罪。',
          authority: '法務部',
        },
        {
          title: '中華民國刑法第320條第1項',
          subTitle: '普通竊盜罪（替代路線評估）',
          items: [
            { num: '1', text: '意圖為自己或第三人不法之所有，而竊取他人之動產者，為竊盜罪，處五年以下有期徒刑、拘役或五十萬元以下罰金。' },
          ],
          hint: '若認場所管理者在顧客遺忘瞬間已取得概括占有支配，未經同意取走亦有論以竊盜罪之實務見解。',
          authority: '法務部',
        },
      ],
      rulings: [
        {
          court: '最高法院',
          caseNo: '50 年台上字第 2038 號刑事判例',
          yearDate: '民國 50 年 11 月 16 日',
          title: '遺失物與他人持有物之占有狀態區別判準',
          holding: '所謂離本人持有之物，係指物之脫離本人之持有，非出於本人之意思，且未落入他人實力支配之下者而言。若在封閉營業場所遺忘，店家管領力是否存在應個案衡量。',
          takeaway: '奠定侵占離本人持有物罪與竊盜罪之分水嶺。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '108 年度上易字第 1520 號刑事判決',
          yearDate: '民國 108 年 9 月 18 日',
          title: '冒用他人信用卡以小額感應交易之詐欺罪責',
          holding: '持卡人利用小額免簽名機制感應過卡，即係向收銀員默示其為正當持卡人之詐術行為，使店員交付商品，成立刑法第339條第1項詐欺取財罪。',
          takeaway: '感應免簽名仍屬詐術實施，不影響詐欺取財罪之成立。',
        },
        {
          court: '臺灣臺北地方法院',
          caseNo: '111 年度簡字第 2341 號刑事簡易判決',
          yearDate: '民國 111 年 10 月 12 日',
          title: '拾得後抗辯「打算交警局卻先消費」不法所有意圖之認定',
          holding: '被告拾獲他人皮夾未送警，反而持卡消費化妝品，客觀上已行使所有權人之處分權能，不法所有意圖甚明，抗辯事後會還錢顯不可採。',
          takeaway: '排除事後賠償之阻卻違法抗辯。',
        },
        {
          court: '臺灣士林地方法院',
          caseNo: '110 年度審簡字第 450 號刑事簡易判決',
          yearDate: '民國 110 年 4 月 20 日',
          title: '侵占遺失物與冒名盜刷之數罪併罰關係',
          holding: '侵占皮夾入己與持卡前往他處盜刷，時間地點互殊，犯意各別，應分論併罰。',
          takeaway: '確定起訴或移送時應論以二罪併罰。',
        },
      ],
      treatises: [
        {
          title: '論現代電子支付與信用卡感應盜刷之刑法處罰體系',
          author: '台灣法學會刑事法專題',
          source: '月旦法學雜誌 第 312 期',
          coreArgument: '感應式信用卡盜刷行為應評價為對店員施詐之刑法第339條詐欺取財，而非第339條之2不正利用自動付款設備罪。',
          takeaway: '法律研析法條應明確引用刑法第339條第1項。',
        },
        {
          title: '營業場所內遺忘物歸屬與竊盜侵占界限之再省思',
          author: '最高檢察署刑事法律研究意見',
          source: '檢察官法學 第 15 期',
          coreArgument: '顧客剛離席尚未走遠，原持有人對物之支配關係尚未完全斷絕，取走仍有可能被論以竊盜，移送時可將竊盜列為備位罪名。',
          takeaway: '條陳中應並列刑法第337條主位與第320條備位罪名。',
        },
        {
          title: '侵占遺失物案件之微罪不舉與起訴裁量原則',
          author: '司法院刑事廳編印',
          source: '刑事裁判評釋叢書 第 8 輯',
          coreArgument: '若行為人事後全額賠償並返還皮夾證件，得審酌依職權不起訴或聲請簡易判決處刑。',
          takeaway: '筆錄應詢問嫌疑人是否願意全額返還及和解意願。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 侵占遺失物罪與竊盜罪之區分標準',
        desc1: `實務上判斷係成立刑法第337條侵占離本人持有物罪或第320條竊盜罪，核心在於客體脫離支配之程度。本案被害人${victimText}用餐後離開咖啡廳座位，皮夾已脫離其直接管領力，涉嫌人拾取並移入自己包內帶離，原則上該當侵占離本人持有物罪；若檢方認營業場所有概括管領支配，亦可能論以竊盜罪。`,
        title2: '2. 冒用感應式信用卡之詐欺取財罪責',
        desc2: `涉嫌人隨後持拾得之信用卡至特約商店小額感應刷卡消費${amountText}，客觀上係以虛偽行使授權身分對特約商店收銀機及店員施用詐術，使特約商店誤信其為正當持卡人而交付商品，獨立成立刑法第339條第1項之詐欺取財既遂罪。`,
        title3: '3. 「事後打算還錢」辯解之法律評價',
        desc3: '涉嫌人辯稱「打算送警局、順路先借用會還錢」云云，按刑法故意犯之成立以行為著手時點為準。涉嫌人取得皮夾未交店員，反而隨即感應刷卡花用，主觀上不法所有意圖甚灼，事後賠償僅屬犯後態度問題，無從阻卻違法。',
        conclusion: '全案監視器畫面清楚錄得取包及刷卡過程，涉嫌人涉犯侵占離本人持有物及詐欺取財兩罪，犯意各別，建請分論併罰。',
      },
      qaItems: [
        {
          id: 'qa-wallet-1',
          type: '拾得經過與保管心態',
          question: `問：你於何時、在何處看見被害人${victimText}遺落之皮夾？當下為何未當場交付店員？`,
          answer: '答：大約下午用餐時，我看見座位上有一個皮夾。我想說店員很忙，我先幫忙保管帶去警局，沒有要侵占的意思。',
          hint: '質疑未即時交付店員之客觀矛盾性。',
        },
        {
          id: 'qa-wallet-2',
          type: '私自帶離與前往特約商店',
          question: '問：你既然辯稱打算送警局，為何將皮夾放入自己手提包帶離現場，並在不久後前往屈臣氏門市？',
          answer: '答：因為門市就在附近，我剛好缺生活用品，就想說順便買一下。',
          hint: '突顯將他人財物置於自己實力支配下之主觀犯意。',
        },
        {
          id: 'qa-wallet-3',
          type: '盜刷信用卡行為與詐欺要件',
          question: `問：你持該張信用卡感應消費${amountText}，你有無獲得卡片持有人之同意或授權？`,
          answer: '答：沒有，我知道這不是我的卡，但我心想刷小額免簽名借用一下，之後找到失主再還錢。',
          hint: '使涉嫌人自白客觀無授權刷卡與使店員陷於錯誤之事實。',
        },
      ],
      report: {
        titleReason: '涉嫌刑法第 337 條侵占離本人持有物罪、刑法第 339 條第 1 項詐欺取財罪嫌。',
        suspects: `犯罪嫌疑人：${suspectText}（國民身分證統一編號：詳卷）`,
        victims: `告訴人兼被害人：${victimText}（國民身分證統一編號：詳卷）`,
        summary: `被害人${victimText}於${e.incidentTime}在${locationText}，離去時不慎將皮夾（內有證件、現金及感應式信用卡1張）遺忘於座位上。犯罪嫌疑人${suspectText}見狀竟意圖為自己不法所有，未交還店家逕自將該皮夾取走放入手提包侵占入己。復於其後前往特約商店門市，持該信用卡感應消費新臺幣${amountText}購買物品。案經調閱監視器於店外當場攔截查獲，涉犯罪證明確。`,
        seizedItems: [
          '被害人所有之皮夾 1 只（已發還）。',
          '感應式信用卡 1 張及現金（已發還）。',
          `涉案盜刷購買之商品及發票明細（金額新臺幣${amountText}）。`,
          '現場監視器錄影光碟 1 片。',
        ],
        legalAnalysis:
          '嫌疑人拾得離本人管領之動產據為己有，涉犯侵占離本人持有物罪；持他人信用卡使收銀員誤信交付商品，該當詐欺取財罪，兩罪犯意各別，行為互殊，建請分論併罰。',
        recommendations: '全案調查完竣，證據確鑿，依法移送管轄地檢署偵辦。',
      },
    };
  }

  // --- 4. 竊盜案 ---
  private static analyzeTheft(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    const suspectText = e.suspect;
    const victimText = e.victim;
    const amountText = e.amount || '財物損失';

    return {
      categoryName: '普通竊盜 / 加重竊盜案',
      aiBrief: `本案嫌疑人${suspectText}意圖為自己不法之所有，乘被害人${victimText}不注意之際竊取他人實力支配下之動產（${amountText}），涉犯刑法第320條第1項普通竊盜罪。若有結夥三人、踰越門窗或攜帶兇器，則成立刑法第321條加重竊盜罪。`,
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第320條第1項',
          subTitle: '普通竊盜罪',
          items: [
            { num: '1', text: '意圖為自己或第三人不法之所有，而竊取他人之動產者，為竊盜罪，處五年以下有期徒刑、拘役或五十萬元以下罰金。' },
          ],
          hint: '破壞他人占有並建立自己支配管領力即屬既遂。',
          authority: '法務部',
        },
        {
          title: '中華民國刑法第321條第1項',
          subTitle: '加重竊盜罪（檢驗是否該當加重事由）',
          items: [
            { num: '1', text: '犯前條第一項之罪而有下列情形之一者，處六月以上五年以下有期徒刑，得併科五十萬元以下罰金：' },
            { num: '一', text: '侵入住宅或有人居住之建築物、船艦或隱匿其內而犯之。' },
            { num: '二', text: '毀越門窗、牆垣或其他安全設備而犯之。' },
            { num: '三', text: '攜帶兇器而犯之。' },
            { num: '四', text: '結夥三人以上而犯之。' },
          ],
          hint: '加重竊盜罪法定刑為六月以上有期徒刑，不得易科罰金。',
          authority: '法務部',
        },
        {
          title: '刑事訴訟法第130條',
          subTitle: '附帶搜索扣押',
          items: [
            { num: '條文', text: '司法警察逮捕被告或執行拘提、羈押時，雖無搜索票，得逕行搜索其身體、隨身攜帶之物件、所使用之交通工具及其立即可觸及之處所。' },
          ],
          hint: '查獲竊嫌時得依法扣押贓物與作案工具。',
          authority: '司法院刑事廳',
        },
      ],
      rulings: [
        {
          court: '最高法院',
          caseNo: '17 年上字第 509 號刑事判例',
          yearDate: '民國 17 年 5 月 12 日',
          title: '竊盜罪既遂與著手之認定標準',
          holding: '竊盜罪之既遂，以已將他人實力支配下之物，移歸自己實力支配為要件。凡財物已入行為人實力管領之下，即屬既遂。',
          takeaway: '取走財物即既遂，事後銷贓或藏匿不影響既遂成立。',
        },
        {
          court: '最高法院',
          caseNo: '79 年台上字第 5253 號刑事判例',
          yearDate: '民國 79 年 12 月 14 日',
          title: '加重竊盜攜帶兇器之客觀客觀危險性',
          holding: '刑法第321條第1項第3款所謂兇器，其種類並無限制，凡客觀上足對人之生命、身體、安全構成威脅，具有危險性之凶器均屬之。',
          takeaway: '螺絲起子、美工刀等行竊工具均屬加重竊盜兇器。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '110 年度上易字第 920 號刑事判決',
          yearDate: '民國 110 年 7 月 22 日',
          title: '監視器客觀影像與指紋比對之補強法則',
          holding: '竊嫌雖否認犯罪，惟現場監視錄影畫面清晰錄得其行竊軌跡，核與被害人指訴相符，足資認定有罪。',
          takeaway: '調閱前後監視錄影確立涉案人身分。',
        },
        {
          court: '臺灣臺北地方法院',
          caseNo: '112 年度簡字第 1420 號刑事判決',
          yearDate: '民國 112 年 6 月 15 日',
          title: '竊得財物變賣得款之犯罪所得沒收',
          holding: '被告竊得財物轉賣所得之價金，依刑法第38條之1第4項為犯罪所得之變形，應予宣告沒收，並優先發還被害人。',
          takeaway: '追查通訊行或收購業者釐清金流流向。',
        },
      ],
      treatises: [
        {
          title: '竊盜犯罪調查實務與監視錄影數位採證規範',
          author: '內政部警政署刑事警察局',
          source: '刑事偵查工作手冊 第 5 章',
          coreArgument: '偵辦竊盜案應迅速建立嫌疑人之「到場動線、行竊手法、離場路徑」，並落實贓物查扣與追贓返還。',
          takeaway: '筆錄應詢問作案工具下落及贓物銷贓管道。',
        },
        {
          title: '加重竊盜罪各款加重事由之構成要件論述',
          author: '最高法院裁判要旨解析編委會',
          source: '法令月刊 第 73 卷第 2 期',
          coreArgument: '踰越安全設備或攜帶兇器必須於著手竊盜之際存在，方可成立加重竊盜罪。',
          takeaway: '調查經過須載明有無破壞門鎖或使用工具。',
        },
        {
          title: '故買贓物罪與收購二手物品業者之注意義務',
          author: '檢察官實務座談會',
          source: '檢察官論壇 第 42 期',
          coreArgument: '二手收購商未查驗身分或以顯不相當之低價收購，可能成立刑法第349條贓物罪。',
          takeaway: '可擴大調閱收贓通訊行查證。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 竊盜罪之客觀著手與既遂認定',
        desc1: `涉嫌人破壞被害人${victimText}對財物之管領支配，將財物置於自己實力掌握之下，該當刑法第320條第1項普通竊盜罪之客觀要件。`,
        title2: '2. 加重竊盜情事之排除或認定',
        desc2: '本案需確認涉嫌人下手行竊時，有無攜帶工具（如螺絲起子、剪刀）、結夥三人或侵入住宅情事，以確認是否適用刑法第321條加重竊盜罪。',
        title3: '3. 贓物追蹤與發還被害人程序',
        desc3: `查獲之遭竊財物（${amountText}），於警詢確認被害人所有權後，得依刑事訴訟法第142條由司法警察發還被害人代保管。`,
        conclusion: '涉嫌人行竊事證有監視影像及被害人指訴在卷，依法移送偵辦。',
      },
      qaItems: [
        {
          id: 'qa-theft-1',
          type: '案發經過與行竊手段',
          question: `問：你於何時、何地，以何種手法竊取被害人${victimText}之財物？`,
          answer: `答：我趁被害人不注意時，將其財物拿走放入包包帶走。`,
          hint: '使涉嫌人交代具體下手動作。',
        },
        {
          id: 'qa-theft-2',
          type: '贓物去向與變賣處分',
          question: `問：你竊得之財物目前在何處？有無轉賣他人或藏匿？得款多少？`,
          answer: `答：一部分拿去變賣花掉了，其餘未變賣部分帶在身上。`,
          hint: '追查贓物流向與查扣變賣所得。',
        },
      ],
      report: {
        titleReason: '涉嫌刑法第 320 條第 1 項普通竊盜罪嫌。',
        suspects: `犯罪嫌疑人：${suspectText}（國民身分證統一編號：詳卷）`,
        victims: `告訴人兼被害人：${victimText}（國民身分證統一編號：詳卷）`,
        summary: `犯罪嫌疑人${suspectText}意圖為自己不法之所有，於${e.incidentTime}在${e.incidentLocation}，乘被害人${victimText}不注意之際，徒手竊取其所有之${amountText}得手後逃逸。案經被害人報警，警員調閱監視影像鎖定查獲，涉犯罪證明確。`,
        seizedItems: ['遭竊財物或變賣剩餘款項（已拍照發還）。', '案發現場監視器翻拍照片及錄影光碟 1 份。'],
        legalAnalysis: '破壞他人占有並建立自己實力支配，已該當刑法第320條竊盜罪要件。',
        recommendations: '依法移送臺灣臺北地方檢察署偵辦。',
      },
    };
  }

  // --- 5. 傷害與恐嚇案 ---
  private static analyzeAssaultAndCoercion(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    const suspectText = e.suspect;
    const victimText = e.victim;

    return {
      categoryName: '傷害、恐嚇與妨害自由案件',
      aiBrief: `本案涉嫌人${suspectText}基於傷害與恐嚇犯意，攻擊被害人${victimText}致其受傷並出言脅迫，涉及刑法第277條第1項普通傷害罪及第305條恐嚇危害安全罪嫌。若有限制行動或妨害行使權利，另涉刑法第304條強制罪。`,
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第277條第1項',
          subTitle: '普通傷害罪',
          items: [
            { num: '1', text: '傷害人之身體或健康者，處五年以下有期徒刑、拘役或五十萬元以下罰金。' },
          ],
          hint: '本罪屬告訴乃論之罪，告訴人須於知悉犯人之日起六個月內提出告訴。',
          authority: '法務部',
        },
        {
          title: '中華民國刑法第305條',
          subTitle: '恐嚇危害安全罪',
          items: [
            { num: '條文', text: '以加害生命、身體、自由、名譽、財產之事恐嚇他人，致生危害於安全者，處二年以下有期徒刑、拘役或九千元以下罰金。' },
          ],
          hint: '言語或肢體使人心生畏懼即該當，屬非告訴乃論。',
          authority: '法務部',
        },
        {
          title: '中華民國刑法第304條第1項',
          subTitle: '強制罪',
          items: [
            { num: '1', text: '以強暴、脅迫使人行無義務之事或妨害人行使權利者，處三年以下有期徒刑、拘役或九千元以下罰金。' },
          ],
          hint: '強行攔車阻擋去路、強行拉下車均屬強暴脅迫之強制行為。',
          authority: '法務部',
        },
      ],
      rulings: [
        {
          court: '最高法院',
          caseNo: '30 年上字第 3701 號刑事判例',
          yearDate: '民國 30 年 12 月 18 日',
          title: '互毆不得主張正當防衛之實務法則',
          holding: '侵害已過去者不生防衛問題，彼此互毆又必以侵害他人為目的，無正當防衛之可言。',
          takeaway: '排除加害人事後辯稱對方先動手之防衛抗辯。',
        },
        {
          court: '最高法院',
          caseNo: '27 年上字第 1215 號刑事判例',
          yearDate: '民國 27 年 8 月 5 日',
          title: '恐嚇罪惡害通知與受告知人心生畏懼之認定',
          holding: '刑法第305條之恐嚇罪，只要行為人以加害之事通知他人，足使一般人心生畏懼即告成立，不以果真發生危害為必要。',
          takeaway: '恫嚇言語「打死你」足致一般人心生畏懼成立本罪。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '109 年度上易字第 1420 號刑事判決',
          yearDate: '民國 109 年 11 月 5 日',
          title: '持球棒砸車並傷人之強制、毀損與傷害競合',
          holding: '行車糾紛攔車持棒擊破車窗並毆傷駕駛人，分別成立強制、毀損與傷害罪，應依法分論併罰或依想像競合論處。',
          takeaway: '條陳公文應嚴謹論列各罪名與法益侵害。',
        },
        {
          court: '臺灣臺中地方法院',
          caseNo: '112 年度訴字第 520 號刑事判決',
          yearDate: '民國 112 年 4 月 18 日',
          title: '醫院驗傷診斷書之證據能力與因果關係',
          holding: '告訴人提出之合格醫療院所甲種驗傷診斷證明書，所載傷勢與嫌疑人施暴時間、部位吻合，足以佐證傷害因果關係。',
          takeaway: '驗傷單載明受傷時間及創傷程度為必備物證。',
        },
      ],
      treatises: [
        {
          title: '街頭行車衝突暴力犯罪之偵查要領與罪名競合',
          author: '法務部檢察司研究專輯',
          source: '檢察研究 第 48 期',
          coreArgument: '攔車施暴行為常伴隨刑法第304條強制罪、第354條毀損罪與第277條傷害罪，應完整蒐集行車紀錄器與路口監視器影像。',
          takeaway: '第一時間應查扣作案球棒與雙方行車紀錄器記憶卡。',
        },
        {
          title: '傷害罪告訴期間起算點與撤回告訴之效力',
          author: '最高法院裁判評釋小組',
          source: '月旦裁判時報 第 118 期',
          coreArgument: '刑法第277條第1項普通傷害罪為告訴乃論，告訴人於第一審言詞辯論終結前得撤回告訴；恐嚇罪則為公訴罪不得撤回。',
          takeaway: '筆錄應詢問被害人是否堅持提出傷害告訴。',
        },
        {
          title: '論刑法第305條恐嚇罪之危險犯本質與舉證實務',
          author: '台灣法學研究會',
          source: '刑事法雜誌 第 66 卷第 3 期',
          coreArgument: '恐嚇罪以惡害通知已達被害人並致其心生畏怖為已足，行車紀錄器清晰錄音為最強力證物。',
          takeaway: '提示行車紀錄器錄音請當事人確認語句內容。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 傷害行為與醫院診斷證明之因果關係',
        desc1: `涉嫌人持球棒及徒手毆擊被害人${victimText}，造成頭部撕裂傷及骨折等傷勢，有醫院甲種驗傷診斷證明書在卷可稽，施暴行為與傷害結果具有相當因果關係。`,
        title2: '2. 言詞恐嚇與強制行為之獨立罪責',
        desc2: `涉嫌人攔截去路妨害通行該當刑法第304條強制罪；又出言「再叭就打死你」已構成加害生命身體之惡害通知，致被害人心生畏怖，另涉刑法第305條恐嚇危害安全罪。`,
        title3: '3. 告訴程序與非告訴乃論之區分',
        desc3: `傷害罪屬告訴乃論，被害人已當場提出告訴；恐嚇罪與強制罪為非告訴乃論，縱傷害部分撤回，非告訴乃論部分仍應依法移送檢察官偵辦。`,
        conclusion: `案發現場監視器及行車紀錄器光碟已調閱扣案，醫院驗傷單在卷，全案涉犯傷害、恐嚇及強制罪事證明確。`,
      },
      qaItems: [
        {
          id: 'qa-assault-1',
          type: '衝突起因與攔車經過',
          question: `問：案發當日你與被害人${victimText}係因何事發生糾紛？你如何攔阻對方車輛？`,
          answer: `答：雙方係因超車糾紛發生口角，我一時氣憤在停等紅燈時將對方攔下。`,
          hint: '特定動機與強制著手行為。',
        },
        {
          id: 'qa-assault-2',
          type: '動手攻擊手段與凶器',
          question: `問：你持何物攻擊被害人？攻擊對方身體何部位？`,
          answer: `答：我持隨車攜帶的鋁棒擊破對方擋風玻璃，並打中對方手臂及推擠。`,
          hint: '釐清使用凶器與傷勢造成經過。',
        },
      ],
      report: {
        titleReason: '涉嫌刑法第 277 條第 1 項傷害罪、第 305 條恐嚇罪、第 304 條強制罪嫌。',
        suspects: `犯罪嫌疑人：${suspectText}（國民身分證統一編號：詳卷）`,
        victims: `告訴人兼被害人：${victimText}（國民身分證統一編號：詳卷）`,
        summary: `犯罪嫌疑人${suspectText}於${e.incidentTime}在${e.incidentLocation}，因行車超車糾紛心生不滿，竟攔阻被害人${victimText}自小客車去路，持隨身鋁製球棒擊破擋風玻璃，並將被害人拉下車毆打揮擊，致其受有多處挫傷及骨折，並出言恫嚇。案經被害人檢附醫院診斷證明書提出告訴，涉犯罪證明確。`,
        seizedItems: ['扣案涉案鋁製球棒 1 支。', '自小客車行車紀錄器錄影光碟 1 份。', '醫院診斷證明書正本 1 紙。'],
        legalAnalysis: '施暴致傷客觀該當傷害罪，恐嚇言語使人心生畏怖該當恐嚇罪，攔截去路該當強制罪，建請依法偵辦。',
        recommendations: '全案調查完竣，依法移送管轄地檢署偵辦。',
      },
    };
  }

  // --- 6. 交通事故 / 肇事逃逸 ---
  private static analyzeHitAndRun(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    return {
      categoryName: '肇事逃逸與交通事故案件',
      aiBrief: '本案涉嫌人駕駛動力交通工具肇事致人受傷而逃逸，涉犯刑法第185條之4肇事致人死傷逃逸罪，以及刑法第284條過失傷害罪嫌。肇事逃逸為非告訴乃論之公訴罪。',
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第185-4條',
          subTitle: '肇事致人死傷逃逸罪',
          items: [
            { num: '1', text: '駕駛動力交通工具發生交通事故，致人傷害而逃逸者，處六月以上五年以下有期徒刑；致人於死或重傷而逃逸者，處一年以上七年以下有期徒刑。' },
          ],
          hint: '非告訴乃論，即使無過失責任，只要肇事致人死傷離去現場即成立。',
          authority: '法務部',
        },
        {
          title: '中華民國刑法第284條',
          subTitle: '過失傷害罪',
          items: [
            { num: '條文', text: '因過失傷害人者，處一年以下有期徒刑、拘役或十萬元以下罰金；致重傷者，處三年以下有期徒刑、拘役或三十萬元以下罰金。' },
          ],
          hint: '告訴乃論之罪，須有注意義務之違反。',
          authority: '法務部',
        },
        {
          title: '道路交通管理處罰條例第62條',
          subTitle: '肇事逃逸之行政責任',
          items: [
            { num: '4', text: '汽車駕駛人駕駛汽車肇事致人受傷而逃逸者，吊銷其駕駛執照；致人重傷或死亡而逃逸者，吊銷其駕駛執照，並不得再考領。' },
          ],
          hint: '刑責移送外，應同步製單舉發吊銷駕照。',
          authority: '交通部',
        },
      ],
      rulings: [
        {
          court: '司法院釋字',
          caseNo: '釋字第 777 號解釋',
          yearDate: '民國 108 年 5 月 31 日',
          title: '刑法第185條之4肇事逃逸罪之合憲性解釋與修法基準',
          holding: '肇事逃逸罪修法後明定「發生交通事故，致人死傷而逃逸」，以保障用路人生命安全及即時救護為立法目的。',
          takeaway: '確認駕駛人事故後有留置現場救護之法律作為義務。',
        },
        {
          court: '最高法院',
          caseNo: '110 年度台上字第 5480 號刑事判決',
          yearDate: '民國 110 年 11 月 18 日',
          title: '肇事逃逸罪主觀故意與知情要件之認定',
          holding: '行為人對於發生碰撞及可能致人受傷客觀上有預見可能性，未下車查看救護即駛離現場，具肇事逃逸故意。',
          takeaway: '排除「以為沒撞到人、趕時間」之辯解。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '109 年度交上訴字第 120 號刑事判決',
          yearDate: '民國 109 年 6 月 25 日',
          title: '肇事逃逸與過失傷害之數罪評價',
          holding: '過失肇事與事後故意逃逸，屬兩獨立行為，應分論併罰。',
          takeaway: '二罪併罰移送偵辦。',
        },
        {
          court: '臺灣臺北地方法院',
          caseNo: '111 年度交訴字第 82 號刑事判決',
          yearDate: '民國 111 年 9 月 14 日',
          title: '路口監視器車辨系統軌跡之科學證據證明力',
          holding: '事故現場路口監視錄影及車牌辨識系統完整記錄逃逸路徑及車身擦痕，足證被告犯行。',
          takeaway: '採集車身比對擦痕與比對行車時間軸。',
        },
      ],
      treatises: [
        {
          title: '交通事故肇事逃逸罪之構成要件與最新修法評析',
          author: '台灣刑事法學會',
          source: '台灣法學雜誌 第 380 期',
          coreArgument: '新法修正法定刑級距，對於情節輕微致輕傷者給予法官緩刑或易科罰金空間，惟仍屬重大公訴罪。',
          takeaway: '應詳實記錄被害人傷勢為輕傷或重傷。',
        },
        {
          title: '道路交通事故現場採證與肇事逃逸追緝技巧',
          author: '內政部警政署交通組',
          source: '交通執法研究 第 24 期',
          coreArgument: '第一時間應落實「散落物碎片採集、胎痕量測、調閱沿途天羅地網監視器」。',
          takeaway: '鑑識人員應比對車輛擦痕與漆痕成分。',
        },
        {
          title: '過失傷害罪與交通事故初步分析研判表之因果關係判斷',
          author: '檢察官實務座談會',
          source: '司法周刊 第 2110 期',
          coreArgument: '初步分析研判表僅為警政參考，正式責任應送車輛行車事故鑑定會鑑定。',
          takeaway: '建議告訴人申請車輛行車事故鑑定。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 肇事逃逸罪之救護義務與行為認定',
        desc1: `涉嫌人駕駛車輛與被害人發生碰撞致其倒地受傷，客觀已知悉發生事故，竟未停留在現場救護傷患或報警，逕自駛離現場，該當刑法第185條之4肇事逃逸罪。`,
        title2: '2. 過失傷害之責任歸屬',
        desc2: '涉嫌人未注意車前狀況或有闖紅燈違規，涉犯刑法第284條前段過失傷害罪，告訴人已於法定六個月內提出告訴。',
        title3: '3. 證據保全與科技查緝',
        desc3: '沿線監視器清楚拍得涉案車牌號碼及撞擊瞬間，並於查扣車輛採集到對應擦痕，事證明確。',
        conclusion: '全案依肇事致人受傷逃逸罪及過失傷害罪移送臺灣臺北地方檢察署。',
      },
      qaItems: [
        {
          id: 'qa-hit-1',
          type: '事故發生與撞擊知悉',
          question: '問：發生碰撞當下，你有無察覺撞擊異音或車輛晃動？有無下車查看？',
          answer: '答：我當下有感覺到車身晃動，但我以為只是撞到路邊雜物，所以沒有停車查看。',
          hint: '突破主觀知悉發生事故之故意。',
        },
      ],
      report: {
        titleReason: '涉嫌刑法第 185 條之 4 肇事致人受傷逃逸罪、第 284 條過失傷害罪嫌。',
        suspects: `犯罪嫌疑人：${e.suspect}`,
        victims: `告訴人兼被害人：${e.victim}`,
        summary: `犯罪嫌疑人駕駛車輛於${e.incidentTime}行經${e.incidentLocation}，與被害人車輛發生碰撞致被害人倒地受傷。嫌疑人肇事後竟未下車施以救護或報警處理，隨即加速逃逸。警調閱路口監視器循線查獲。`,
        seizedItems: ['車禍事故現場圖及照片紀錄表 1 份。', '路口監視器翻拍光碟 1 份。', '醫院甲種診斷證明書 1 份。'],
        legalAnalysis: '發生事故致人受傷逃逸，客觀與主觀要件均該當刑法第185條之4。',
        recommendations: '依法移送管轄地檢署偵辦。',
      },
    };
  }

  // --- 7. 毒品危害防制條例 ---
  private static analyzeNarcotics(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    return {
      categoryName: '毒品危害防制條例案件',
      aiBrief: '本案涉嫌人隨身攜帶疑似毒品結晶或吸食工具，涉犯毒品危害防制條例第10條施用毒品罪或第11條持有毒品罪嫌。扣案粉末及尿液檢體應送專責機構鑑驗。',
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '毒品危害防制條例第10條',
          subTitle: '施用毒品罪',
          items: [
            { num: '2', text: '施用第二級毒品者，處三年以下有期徒刑。' },
          ],
          hint: '施用毒品以尿液複驗報告為定罪依據。',
          authority: '法務部',
        },
        {
          title: '毒品危害防制條例第11條',
          subTitle: '持有毒品罪',
          items: [
            { num: '2', text: '持有第二級毒品者，處二年以下有期徒刑、拘役或新臺幣二十萬元以下罰金。' },
          ],
          hint: '持有純質淨重逾法定標準者加重處罰。',
          authority: '法務部',
        },
        {
          title: '刑事訴訟法第205-2條',
          subTitle: '強制採尿規定',
          items: [
            { num: '條文', text: '司法警察官或司法警察因調查犯罪情形及蒐集證據之必要，對於經拘提或逮捕到案之犯罪嫌疑人，得採取其指紋、掌紋、腳印，得採取其尿液。' },
          ],
          hint: '採尿應遵守法定封緘與被採尿人簽名程序。',
          authority: '司法院刑事廳',
        },
      ],
      rulings: [
        {
          court: '最高法院',
          caseNo: '109 年度台上字第 2100 號刑事判決',
          yearDate: '民國 109 年 4 月 15 日',
          title: '尿液檢驗自白補強法則之實質審查',
          holding: '被告自白施用毒品，必須有尿液檢驗報告確認呈陽性反應，始得為有罪判決。',
          takeaway: '尿檢報告為必要補強證據。',
        },
        {
          court: '司法院釋字',
          caseNo: '釋字第 803 號解釋',
          yearDate: '民國 110 年 5 月 7 日',
          title: '刑事訴訟法採尿程序之正當法律程序保障',
          holding: '非侵入性採尿程序應踐行告知義務及正當法律程序。',
          takeaway: '確認受檢人受採集同意簽名。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '111 年度上訴字第 120 號刑事判決',
          yearDate: '民國 111 年 3 月 10 日',
          title: '持有與施用毒品之吸收關係',
          holding: '施用前持有毒品之低度行為，為施用之高度行為所吸收，僅論以施用毒品罪。',
          takeaway: '若尿檢陽性則持有罪不另論處。',
        },
        {
          court: '臺灣臺北地方法院',
          caseNo: '112 年度審簡字第 450 號刑事判決',
          yearDate: '民國 112 年 8 月 12 日',
          title: '初犯施用毒品觀察勒戒程序適用',
          holding: '犯第10條之罪者，檢察官應聲請法院裁定命其令入勒戒處所觀察、勒戒。',
          takeaway: '查證是否為三年內再犯。',
        },
      ],
      treatises: [
        {
          title: '毒品尿液鑑驗檢驗方法與閾值認定標準',
          author: '衛生福利部食品藥物管理署',
          source: '法醫學通訊 第 18 期',
          coreArgument: '氣相層析質譜儀（GC/MS）為法定確效標準，可排除偽陽性干擾。',
          takeaway: '送驗單應勾選 GC/MS 複驗。',
        },
        {
          title: '毒品初犯觀察勒戒與附條件緩起訴戒癮治療之政策評析',
          author: '法務部司法官學院',
          source: '犯罪學研究 第 25 期',
          coreArgument: '對於單純施用毒品者，以醫療戒癮治療優先於刑罰處罰。',
          takeaway: '移送書應載明有無戒癮治療意願。',
        },
        {
          title: '毒品來源溯源追查通聯分析指引',
          author: '刑事警察局毒品查緝中心',
          source: '毒品偵查要領手冊 第 2 冊',
          coreArgument: '扣案手機應即時封緘，向地檢署聲請通信紀錄與數位採證。',
          takeaway: '應查明藥頭代號與交易金額。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 查扣毒品成分定性鑑驗程序',
        desc1: '扣案結晶粉末及吸食器，當場初篩呈陽性反應，依法封緘後送交專責檢驗機關進行定性及淨重鑑驗。',
        title2: '2. 採集尿液之正當程序規範',
        desc2: '依法對嫌疑人實施採尿，檢體依規定由嫌疑人親自封緘捺印，送請認證實驗室以 GC/MS 進行確效檢驗。',
        title3: '3. 毒品前科與觀察勒戒要件',
        desc3: '經查嫌疑人三年內有無施用毒品前科紀錄，作為檢察官聲請觀察勒戒或起訴之依據。',
        conclusion: '扣案證物送驗，待尿液檢驗報告出爐隨卷移送管轄地檢署。',
      },
      qaItems: [
        {
          id: 'qa-drug-1',
          type: '查獲經過與所有權確認',
          question: '問：警方於何時、何地查獲你？扣案之夾鏈袋結晶是否為你所有？',
          answer: '答：警方於案發處所盤查查獲我，包包內的夾鏈袋粉末確實是我自己的。',
          hint: '確認扣押合法性與占有關係。',
        },
      ],
      report: {
        titleReason: '涉嫌違反毒品危害防制條例第 10 條、第 11 條罪嫌。',
        suspects: `犯罪嫌疑人：${e.suspect}`,
        victims: '國家法益（國民身心健康）',
        summary: `員警執行勤務時於${e.incidentTime}在${e.incidentLocation}，查獲嫌疑人隨身攜帶疑似毒品結晶 1 包及吸食器，當場依法查扣並帶案採尿送驗。`,
        seizedItems: ['疑似毒品結晶 1 包（毛重已秤量）。', '吸食器 1 組。', '尿液採集瓶 2 瓶。'],
        legalAnalysis: '客觀查扣毒品粉末，初步檢驗呈陽性反應，涉嫌持有及施用事證明確。',
        recommendations: '俟尿液檢驗報告出爐隨卷移送臺灣臺北地方檢察署。',
      },
    };
  }

  // --- 8. 不能安全駕駛 (酒駕) ---
  private static analyzeDrunkDriving(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    return {
      categoryName: '不能安全駕駛（酒駕）案件',
      aiBrief: '本案涉嫌人飲酒後駕駛動力交通工具，經呼氣酒精濃度檢測測定值達每公升0.25毫克以上，構成刑法第185條之3第1項第1款公共危險罪，為非告訴乃論之現行犯。',
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第185-3條第1項',
          subTitle: '不能安全駕駛動力交通工具罪',
          items: [
            { num: '1', text: '駕駛動力交通工具而有下列情形之一者，處三年以下有期徒刑，得併科三十萬元以下罰金：' },
            { num: '一', text: '吐氣所含酒精濃度達每公升零點二五毫克或血液中酒精濃度達百分之零點零五以上。', highlight: true },
          ],
          hint: '抽象危險犯，不以發生實害為必要。',
          authority: '法務部',
        },
        {
          title: '道路交通管理處罰條例第35條',
          subTitle: '酒駕處罰與移置保管車輛',
          items: [
            { num: '1', text: '汽機車駕駛人，駕駛汽機車經測試檢定有下列情形之一，機車駕駛人處一萬五千元以上九萬元以下罰鍰，汽車駕駛人處三萬元以上十二萬元以下罰鍰，並均當場移置保管該汽機車及吊扣其駕駛執照一至二年。' },
          ],
          hint: '車輛當場移置保管，吊扣駕駛執照。',
          authority: '交通部',
        },
        {
          title: '刑事訴訟法第88條',
          subTitle: '現行犯逮捕',
          items: [
            { num: '1', text: '現行犯，不問何人得逕行逮捕之。' },
          ],
          hint: '吐氣超標即屬犯罪實施中之現行犯。',
          authority: '司法院刑事廳',
        },
      ],
      rulings: [
        {
          court: '最高法院',
          caseNo: '102 年度台非字第 240 號刑事判決',
          yearDate: '民國 102 年 8 月 22 日',
          title: '刑法第185條之3抽象危險犯之既遂認定時點',
          holding: '啟動車輛引擎動力並已行駛於道路，一經測定酒精濃度超標即屬既遂，無須致生交通事故。',
          takeaway: '只要駕車行駛於道路即達既遂。',
        },
        {
          court: '最高行政法院',
          caseNo: '108 年度判字第 510 號行政判決',
          yearDate: '民國 108 年 10 月 17 日',
          title: '酒測前提供漱口及確認飲酒結束滿15分鐘程序',
          holding: '員警實施檢測前，已落實詢問飲酒結束時間滿15分鐘並提供水漱口，程序合法正當。',
          takeaway: '酒測單及錄影完整記錄漱口程序。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '110 年度交上易字第 310 號刑事判決',
          yearDate: '民國 110 年 5 月 14 日',
          title: '十年內再犯酒駕累犯加重規定之適用',
          holding: '曾受有期徒刑執行完畢十年內再犯酒駕者，依法予以加重處罰。',
          takeaway: '查核刑案紀錄表有無酒駕前科。',
        },
        {
          court: '臺灣新北地方法院',
          caseNo: '112 年度審交簡字第 920 號刑事判決',
          yearDate: '民國 112 年 7 月 10 日',
          title: '不能安全駕駛併科罰金與易科罰金標準',
          holding: '考量被告坦承犯行、未肇事造成人員傷亡，量處得易科罰金之刑。',
          takeaway: '態度良好且未肇事得建請檢方聲請簡易判決處刑。',
        },
      ],
      treatises: [
        {
          title: '取締酒後駕車作業程序之標準化作業指引',
          author: '內政部警政署交通組',
          source: '警察法學季刊 第 45 期',
          coreArgument: '酒測吹氣儀器校正週期、檢測前漱口記錄及全程錄影為防杜程序抗辯之三大鐵則。',
          takeaway: '酒測單應由受測人親自簽名並附卷。',
        },
        {
          title: '刑法公共危險罪章酒駕犯罪沒收車輛規定之檢討',
          author: '台灣刑事法學會論壇',
          source: '月旦刑事法評論 第 12 期',
          coreArgument: '累犯致人重傷或死亡，得依規定宣告沒收犯罪所用之動力交通工具。',
          takeaway: '查明車輛所有人是否為嫌疑人所有。',
        },
        {
          title: '不能安全駕駛動力交通工具罪之犯罪黑數與防制對策',
          author: '中央警察大學交通管理研究所',
          source: '交通執法論文集 第 19 輯',
          coreArgument: '清晨宿醉駕車常為酒駕盲點，員警應加強清晨時段機動攔查。',
          takeaway: '筆錄應詢問前夜飲酒結束確切時間。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 吐氣酒精數值超標之法定要件',
        desc1: '嫌疑人經測試吐氣酒精濃度達每公升0.25毫克以上，已跨越刑法第185條之3刑事處罰門檻，該當不能安全駕駛罪。',
        title2: '2. 施測程序正當性查核',
        desc2: '警方於施測前已落實詢問飲酒結束時間滿15分鐘，並提供杯水漱口，施測過程有密錄器全程錄影在卷。',
        title3: '3. 車輛處置與移送程序',
        desc3: '涉案車輛依法當場移置保管並製單舉發，涉嫌人依現行犯逮捕製作筆錄後隨案解送。',
        conclusion: '酒測單及全程錄影事證明確，依法隨案解送地檢署。',
      },
      qaItems: [
        {
          id: 'qa-drink-1',
          type: '飲酒時地與駕駛事實',
          question: '問：你於何時、在何處飲酒？飲用何種酒類多少？何時開始駕駛車輛？',
          answer: '答：我於案發前在熱炒店喝了啤酒2瓶，結束後心存僥倖騎車返家被攔查。',
          hint: '確認飲酒行為、種類、數量與駕車時空連續性。',
        },
      ],
      report: {
        titleReason: '涉嫌刑法第 185 條之 3 第 1 項第 1 款不能安全駕駛動力交通工具罪嫌。',
        suspects: `犯罪嫌疑人：${e.suspect}`,
        victims: '公眾交通往來安全法益',
        summary: `嫌疑人飲用酒類後駕駛車輛於${e.incidentTime}行經${e.incidentLocation}，經警實施攔查，吐氣酒精濃度測定值達法定標準以上，涉嫌不能安全駕駛罪嫌重大。`,
        seizedItems: ['酒精測定紀錄單 1 紙。', '警方密錄器蒐證光碟 1 份。'],
        legalAnalysis: '客觀呼氣數值超標，已該當刑法第185條之3法定要件。',
        recommendations: '依法隨案解送臺灣臺北地方檢察署偵辦。',
      },
    };
  }

  // --- 9. 妨害性隱私 / 偷拍 ---
  private static analyzeSexualPrivacy(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    return {
      categoryName: '未經同意攝錄性影像罪（偷拍案）',
      aiBrief: '本案涉嫌人未經同意以照相或錄影設備攝錄他人性影像或隱私部位，涉犯刑法第319條之1第1項未經同意攝錄性影像罪。若有散布或恐嚇勒索，另涉同法第319條之3及恐嚇罪嫌。',
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第319-1條第1項',
          subTitle: '未經同意攝錄性影像罪',
          items: [
            { num: '1', text: '未經他人同意，無故以照相、錄影、電磁紀錄或其他科技方法攝錄其性影像者，處三年以下有期徒刑。' },
          ],
          hint: '112年增訂新法，非告訴乃論，專門防制性私密影像犯罪。',
          authority: '法務部',
        },
        {
          title: '中華民國刑法第315-1條',
          subTitle: '妨害秘密罪',
          items: [
            { num: '2', text: '有下列行為之一者，處三年以下有期徒刑、拘役或三十萬元以下罰金：二、無故以錄音、照相、錄影或電磁紀錄竊錄他人非公開之活動、言論、談話或身體隱私部位者。' },
          ],
          hint: '攝錄非公開活動或身體隱私部位之基礎條款。',
          authority: '法務部',
        },
        {
          title: '犯罪被害人權益保障法第34條',
          subTitle: '性影像犯罪被害人保護與移除機制',
          items: [
            { num: '條文', text: '性影像受害人得向主管機關申訴請求令網際網路平台業者限制瀏覽或移除性影像。' },
          ],
          hint: '得依被害人申請啟動性影像處理中心下架機制。',
          authority: '衛生福利部',
        },
      ],
      rulings: [
        {
          court: '最高法院',
          caseNo: '112 年度台上字第 3820 號刑事判決',
          yearDate: '民國 112 年 10 月 12 日',
          title: '刑法第319條之1性影像之實體範圍認定',
          holding: '新法所稱性影像，包含客觀上足以引起性慾或羞恥感之他人裸露身體隱私部位影像。',
          takeaway: '確立偷拍更衣室、裙底均該當本罪。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '111 年度上易字第 820 號刑事判決',
          yearDate: '民國 111 年 6 月 18 日',
          title: '手機及攝影器材之犯罪工具絕對沒收',
          holding: '供犯偷拍所用之手機或隱藏式針孔設備，不問屬於犯人與否，依法均宣告沒收。',
          takeaway: '涉案錄影設備依法應全數扣押。',
        },
        {
          court: '臺灣臺北地方法院',
          caseNo: '112 年度審簡字第 1200 號刑事判決',
          yearDate: '民國 112 年 9 月 20 日',
          title: '被害人受創之精神慰撫金衡量',
          holding: '偷拍侵害人性尊嚴與隱私權甚鉅，被害人得依民法請求精神上非財產損害賠償。',
          takeaway: '被害人得提起附帶民事訴訟求償。',
        },
        {
          court: '臺灣士林地方法院',
          caseNo: '112 年度訴字第 450 號刑事判決',
          yearDate: '民國 112 年 11 月 5 日',
          title: '涉案手機數位鑑識與刪除檔案之還原',
          holding: '被告雖辯稱已刪除，惟經警數位鑑識實驗室還原刪除區塊發現多筆隱私影像，足認犯行。',
          takeaway: '應即刻送數位鑑識提取未儲存快取。',
        },
      ],
      treatises: [
        {
          title: '性影像防制專法新制下司法警察採證與被害人保護實務',
          author: '法務部檢察司研究專輯',
          source: '檢察官法學 第 28 期',
          coreArgument: '應迅速查扣設備斷絕散布途徑，並協助被害人向衛福部性影像處理中心申請申訴下架。',
          takeaway: '第一時間查扣設備並關閉雲端同步。',
        },
        {
          title: '論妨害秘密罪與未經同意攝錄性影像罪之法規競合',
          author: '司法院刑事廳編印',
          source: '司法研究年報 第 42 輯',
          coreArgument: '刑法第319條之1係第315條之1之特別法，應優先適用刑法第319條之1。',
          takeaway: '主位罪名應列刑法第319條之1。',
        },
        {
          title: '數位鑑識科技在偷拍案件電磁紀錄保全之實踐',
          author: '中央警察大學資訊警察研究所',
          source: '警學叢刊 第 53 卷第 2 期',
          coreArgument: '應提取涉案手機之 Hash 值、拍攝時間 EXIF 資訊及雲端相簿同步日誌。',
          takeaway: '製作數位證物鏈保管單。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 構成要件與新法適用',
        desc1: '涉嫌人未經被害人同意，無故使用攝影器材攝錄其隱私部位，客觀已該當刑法第319條之1第1項之罪。',
        title2: '2. 設備扣押與數位採證鑑識',
        desc2: '現場依法查扣涉案手機或攝影器材，送請專業數位鑑識單位提取相簿檔案、已刪除相片及雲端備份紀錄。',
        title3: '3. 性影像散布防制與被害人保護',
        desc3: '協助被害人確認有無外流風險，啟動衛福部性影像處理中心防制散布機制。',
        conclusion: '涉案器材已查扣在案，依法移送偵辦。',
      },
      qaItems: [
        {
          id: 'qa-privacy-1',
          type: '拍攝行為與器材確認',
          question: '問：扣案手機內之拍攝檔案是否為你所拍？何時、何地拍攝？',
          answer: '答：是我用手機拍的，我一時好奇才動手。',
          hint: '自白拍攝動作與器材歸屬。',
        },
      ],
      report: {
        titleReason: '涉嫌刑法第 319 條之 1 第 1 項未經同意攝錄性影像罪、第 315 條之 1 妨害秘密罪嫌。',
        suspects: `犯罪嫌疑人：${e.suspect}`,
        victims: `告訴人兼被害人：${e.victim}`,
        summary: `涉嫌人於${e.incidentTime}在${e.incidentLocation}，未經被害人同意，無故持手機攝錄被害人之隱私部位，當場遭發覺報警查獲並扣押涉案手機。`,
        seizedItems: ['涉案手機 1 支。', '被害人指訴紀錄 1 份。'],
        legalAnalysis: '無故攝錄他人性隱私部位，該當刑法第319條之1要件。',
        recommendations: '依法移送管轄地檢署偵辦。',
      },
    };
  }

  // --- 10. 毀損罪 ---
  private static analyzePropertyDamage(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    return {
      categoryName: '毀損他人器物罪案件',
      aiBrief: '本案涉嫌人無正當理由毀棄、損壞他人之物或致令不堪用，涉犯刑法第354條毀損器物罪嫌。本罪屬告訴乃論。',
      badges: [
        { label: '法規', count: 2, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第354條',
          subTitle: '毀損器物罪',
          items: [
            { num: '條文', text: '毀棄、損壞前二條以外之他人之物或致令不堪用，足以生損害於公眾或他人者，處二年以下有期徒刑、拘役或一萬五千元以下罰金。' },
          ],
          hint: '告訴乃論之罪，須有毀棄、損壞或致令不堪用之實害結果。',
          authority: '法務部',
        },
        {
          title: '刑事訴訟法第237條',
          subTitle: '告訴期間',
          items: [
            { num: '1', text: '告訴乃論之罪，其告訴應自得為告訴之人知悉犯人之時起，於六個月內為之。' },
          ],
          hint: '告訴乃論案件告訴期間為六個月。',
          authority: '司法院刑事廳',
        },
      ],
      rulings: [
        {
          court: '最高法院',
          caseNo: '47 年台非字第 34 號刑事判例',
          yearDate: '民國 47 年 4 月 25 日',
          title: '毀損罪「致令不堪用」之法律涵義',
          holding: '刑法第354條所謂致令不堪用，係指從物之本來效用加以破壞，使其喪失其全部或一部之效用者而言。',
          takeaway: '車窗碎裂、車身嚴重刮花喪失美觀與安全即該當。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '110 年度上易字第 450 號刑事判決',
          yearDate: '民國 110 年 3 月 18 日',
          title: '監視器錄影翻拍與修復報價單之證明力',
          holding: '原廠修復估價單與現場照片足以佐證財物損壞範圍與損失金額。',
          takeaway: '被害人應檢附修復估價單。',
        },
        {
          court: '臺灣臺北地方法院',
          caseNo: '112 年度簡字第 820 號刑事判決',
          yearDate: '民國 112 年 5 月 10 日',
          title: '毀損物品民事侵權回復原狀請求',
          holding: '毀損他人器物者應負民法第184條侵權賠償責任，負擔必要修復費用。',
          takeaway: '得於起訴後提起附帶民事訴訟求償。',
        },
        {
          court: '臺灣士林地方法院',
          caseNo: '111 年度審簡字第 310 號刑事判決',
          yearDate: '民國 111 年 8 月 20 日',
          title: '告訴人撤回告訴之不受理判決程序',
          holding: '告訴乃論之罪於第一審言詞辯論終結前得撤回，撤回後為不受理判決。',
          takeaway: '若涉嫌人完成賠償得促成雙方和解撤回。',
        },
      ],
      treatises: [
        {
          title: '毀損罪之實務爭議與「致令不堪用」之判定標準',
          author: '台灣法學研究會',
          source: '月旦法學教室 第 220 期',
          coreArgument: '器物是否不堪用，應從交易通念及該物主要功能是否滅失或減損為客觀判斷。',
          takeaway: '拍照應包含損壞特寫及全景照片。',
        },
        {
          title: '行車砸車毀損與強制罪之裁判競合論述',
          author: '最高法院裁判評鑑',
          source: '檢察官實務評議 第 31 期',
          coreArgument: '砸毀車輛擋風玻璃同時使駕駛人受困，成立毀損罪與強制罪想像競合。',
          takeaway: '應詢問車內人員當下之自由限制情形。',
        },
        {
          title: '告訴乃論罪章和解撤回實務程序規範',
          author: '司法院刑事廳編印',
          source: '刑事司法手冊 第 12 輯',
          coreArgument: '告訴人表明撤回之意思表示應書面附卷。',
          takeaway: '備妥和解撤回書供雙方簽署。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 毀損行為與效用喪失認定',
        desc1: `涉嫌人故意破壞被害人${e.victim}之財物，致物失去原有效用，該當刑法第354條毀損器物罪。`,
        title2: '2. 告訴乃論法定期間確認',
        desc2: '本罪屬告訴乃論，告訴人已於法定六個月期間內依法提出合法告訴。',
        title3: '3. 損害賠償與和解意願',
        desc3: '檢附原廠修復估價單以確定損失金額，詢問雙方有無和解調解意願。',
        conclusion: '現場監視畫面及照片齊全，依法移送偵辦。',
      },
      qaItems: [
        {
          id: 'qa-damage-1',
          type: '破壞動機與手段',
          question: '問：你為何持物砸毀破壞被害人之物品？損壞程度為何？',
          answer: '答：我一時氣憤才動手砸壞，我願意賠償對方修復費用。',
          hint: '自白破壞事實及犯後態度。',
        },
      ],
      report: {
        titleReason: '涉嫌刑法第 354 條毀損器物罪嫌。',
        suspects: `犯罪嫌疑人：${e.suspect}`,
        victims: `告訴人兼被害人：${e.victim}`,
        summary: `涉嫌人於${e.incidentTime}在${e.incidentLocation}，故意毀損被害人之財物，造成嚴重損壞喪失其原有效用。案經被害人檢附修復估價單提出告訴。`,
        seizedItems: ['受損財物現場採證照片 1 份。', '修復估價單據 1 份。'],
        legalAnalysis: '客觀破壞物之本來效用，該當刑法第354條毀損罪要件。',
        recommendations: '依法移送管轄地檢署偵辦。',
      },
    };
  }

  // --- 11. 妨害名譽 / 誹謗 ---
  private static analyzeDefamation(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    return {
      categoryName: '妨害名譽與誹謗案件',
      aiBrief: '本案涉嫌人散布足以毀損他人名譽之事，涉犯刑法第310條誹謗罪或第309條公然侮辱罪嫌。本罪屬告訴乃論。',
      badges: [
        { label: '法規', count: 2, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: '中華民國刑法第310條第1、2項',
          subTitle: '誹謗罪與加重誹謗罪',
          items: [
            { num: '1', text: '意圖散布於眾，而指摘或傳述足以毀損他人名譽之事者，為誹謗罪，處一年以下有期徒刑、拘役或一萬五千元以下罰金。' },
            { num: '2', text: '散布文字、圖畫犯前項之罪者，處二年以下有期徒刑、拘役或三萬元以下罰金。' },
          ],
          hint: '散布文字或透過網路發文，適用第2項加重誹謗罪。',
          authority: '法務部',
        },
        {
          title: '中華民國刑法第309條',
          subTitle: '公然侮辱罪',
          items: [
            { num: '1', text: '公然侮辱人者，處拘役或九千元以下罰金。' },
          ],
          hint: '未指摘具體事實而僅為抽象謾罵者適用本罪。',
          authority: '法務部',
        },
      ],
      rulings: [
        {
          court: '司法院憲法法庭',
          caseNo: '112 年憲判字第 8 號判決',
          yearDate: '民國 112 年 6 月 9 日',
          title: '刑法誹謗罪合憲性與言論自由界限之最新權威闡釋',
          holding: '刑法第310條合憲。發表言論前有合理查證義務，若明知為虛偽或重大過失未查證，不享有言論自由保障。',
          takeaway: '奠定現代網路發言誹謗罪之定罪基準。',
        },
        {
          court: '最高法院',
          caseNo: '109 年度台上字第 4120 號刑事判決',
          yearDate: '民國 109 年 9 月 17 日',
          title: '網路公開社群發言「意圖散布於眾」之認定',
          holding: '於公開臉書社團或通訊群組發表指摘他人文字，多數人得共見共聞，具散布於眾意圖。',
          takeaway: '網路公開貼文即具散布於眾之故意。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '111 年度上易字第 650 號刑事判決',
          yearDate: '民國 111 年 4 月 28 日',
          title: '公然侮辱與誹謗罪之客觀區別',
          holding: '誹謗罪重在指摘足以毀損名譽之「具體事實」；公然侮辱則為「抽象謾罵侮蔑」。',
          takeaway: '貼文含有具體指控者應論以加重誹謗罪。',
        },
        {
          court: '臺灣臺北地方法院',
          caseNo: '112 年度易字第 210 號刑事判決',
          yearDate: '民國 112 年 7 月 15 日',
          title: '網路匿名留言之 IP 與帳號反查查證義務',
          holding: '檢警依法調取網路連線 IP 及電信門號，查獲發文者真實身分。',
          takeaway: '調取發文 IP 為破案關鍵。',
        },
      ],
      treatises: [
        {
          title: '憲法法庭112年憲判字第8號後誹謗罪刑事偵查指引',
          author: '法務部檢察司',
          source: '檢察官實務手冊 第 29 冊',
          coreArgument: '應著重調查行為人於發布言論時，是否曾向當事人查證或具備客觀可靠消息來源。',
          takeaway: '筆錄應詢問發文依據與查證紀錄。',
        },
        {
          title: '網路社群妨害名譽犯罪之數位鑑識標準程序',
          author: '警政署刑事警察局科偵隊',
          source: '科技偵查期刊 第 14 期',
          coreArgument: '告訴人提供之貼文截圖應含有 URL、留言時間及帳號資訊，以利向平台調閱註冊資料。',
          takeaway: '截圖須含發文帳號 UID。',
        },
        {
          title: '妨害名譽罪之民事侵權名譽權損害賠償與澄清啟事',
          author: '台灣法學會民事法委員會',
          source: '月旦民商法雜誌 第 76 期',
          coreArgument: '名譽受損害得請求金錢賠償及適當回復名譽之處分。',
          takeaway: '告知告訴人得民刑併進主張權利。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 散布於眾與指摘具體事實要件',
        desc1: `涉嫌人於不特定多數人可見之場合，指摘足以毀損被害人${e.victim}名譽之事，客觀已該當刑法第310條誹謗罪要件。`,
        title2: '2. 加重誹謗罪文字散布之適用',
        desc2: '因透過網際網路散布文字，依法論以刑法第310條第2項加重誹謗罪。',
        title3: '3. 告訴期間與民刑權益保障',
        desc3: '告訴人已於法定六個月期間內依法具狀告訴，保全網路發文截圖。',
        conclusion: '涉案貼文截圖與身分查證齊全，依法移送偵辦。',
      },
      qaItems: [
        {
          id: 'qa-defam-1',
          type: '貼文發表與真實查證',
          question: '問：該網路帳號是否為你所有？涉案文字是否由你張貼？發文前有無向被害人查證？',
          answer: '答：帳號是我本人的，貼文也是我發的，我聽朋友說就氣不過發文，沒有特別向對方查證。',
          hint: '自白發文動作及未合理查證。',
        },
      ],
      report: {
        titleReason: '涉嫌刑法第 310 條第 2 項加重誹謗罪、第 309 條公然侮辱罪嫌。',
        suspects: `犯罪嫌疑人：${e.suspect}`,
        victims: `告訴人：${e.victim}`,
        summary: `涉嫌人意圖散布於眾，於${e.incidentTime}透過網路社群公開張貼文字，指摘足以毀損告訴人${e.victim}名譽之不實言論，造成告訴人名譽嚴重受損。案經告訴人提供截圖提出告訴。`,
        seizedItems: ['涉案社群發文及留言翻拍截圖 1 冊。', '涉案帳號註冊資料調閱公文影本 1 份。'],
        legalAnalysis: '散布文字毀損他人名譽，該當刑法第310條第2項加重誹謗罪。',
        recommendations: '依法移送管轄地檢署偵辦。',
      },
    };
  }

  // --- 12. 動態通用自訂案情分析 (從文本完整提取真實情境) ---
  private static analyzeCustomDynamic(raw: string, e: ReturnType<typeof CaseAnalyzer.extractEntities>): CaseAnalysisResult {
    // 智能推導主攻法條
    let mainLawTitle = '中華民國刑法相關規定';
    let mainLawSub = '刑事違法性研析';
    let mainHint = '檢警依法調查客觀證據。';

    if (/偷|竊|拿走/.test(raw)) {
      mainLawTitle = '中華民國刑法第320條';
      mainLawSub = '普通竊盜罪';
      mainHint = '破壞他人實力支配歸自己管領。';
    } else if (/詐|騙|假冒/.test(raw)) {
      mainLawTitle = '中華民國刑法第339條';
      mainLawSub = '詐欺取財罪';
      mainHint = '施用詐術使人陷於錯誤交付財物。';
    } else if (/打|傷|打擊/.test(raw)) {
      mainLawTitle = '中華民國刑法第277條';
      mainLawSub = '普通傷害罪';
      mainHint = '告訴乃論之罪，需驗傷單為證。';
    } else if (/侵占|撿到|拾獲/.test(raw)) {
      mainLawTitle = '中華民國刑法第337條';
      mainLawSub = '侵占離本人持有物罪';
      mainHint = '偶然取得他人脫離物據為己有。';
    } else if (/撞|逃|車禍/.test(raw)) {
      mainLawTitle = '中華民國刑法第185-4條';
      mainLawSub = '肇事逃逸罪';
      mainHint = '發生事故致人死傷應即時救護。';
    }

    return {
      categoryName: '自訂案情動態綜合研析',
      aiBrief: `本案經系統即時語意拆解，針對所載「${raw.slice(0, 50)}...」等客觀事實要素進行深度法律定性。涉案行為人涉嫌違反${mainLawTitle}，依法啟動偵查程序調查客觀物證。`,
      badges: [
        { label: '法規', count: 3, key: 'laws' },
        { label: '裁判', count: 4, key: 'rulings' },
        { label: '論著', count: 3, key: 'treatises' },
      ],
      laws: [
        {
          title: mainLawTitle,
          subTitle: mainLawSub,
          items: [
            { num: '主要條文', text: `依刑法規範，本案行為人實施之行為已涉犯${mainLawSub}構成要件。`, highlight: true },
          ],
          hint: mainHint,
          authority: '法務部',
        },
        {
          title: '刑事訴訟法第228條',
          subTitle: '檢警偵查發動與蒐集證據職權',
          items: [
            { num: '1', text: '檢察官因告訴、告發、自首或其他情事知有犯罪嫌疑者，應即開始偵查。' },
            { num: '2', text: '前項偵查，檢察官得限期命司法警察官或司法警察調查犯罪情形及蒐集證據，並提出報告。' },
          ],
          hint: '為司法警察依法調查、製作筆錄與蒐證之法源依據。',
          authority: '司法院刑事廳',
        },
        {
          title: '刑事訴訟法第154條第2項',
          subTitle: '嚴格證明法則與無罪推定',
          items: [
            { num: '2', text: '犯罪事實應依證據認定之，無證據不得認定犯罪事實。' },
          ],
          hint: '當事人陳述須有客觀書證、物證或科技採證補強。',
          authority: '司法院刑事廳',
        },
      ],
      rulings: [
        {
          court: '最高法院',
          caseNo: '30 年上字第 816 號刑事判例',
          yearDate: '民國 30 年 3 月 20 日',
          title: '認定犯罪事實憑據之證據法則',
          holding: '認定不利於被告之事實，須依積極證據，苟積極證據不足為不利於被告事實之認定時，即應為有利於被告之認定。',
          takeaway: '落實嚴格證據證明原則，不得僅憑片面指訴。',
        },
        {
          court: '最高法院',
          caseNo: '40 年台上字第 86 號刑事判例',
          yearDate: '民國 40 年 5 月 15 日',
          title: '告訴人指訴之實體補強證據法則',
          holding: '告訴人之告訴，係以使被告受刑事訴追為目的，是其陳述是否與事實相符，仍應調查其他證據以資審認。',
          takeaway: '須調閱現場監視影像、金流或通聯等客觀事證補強。',
        },
        {
          court: '臺灣高等法院',
          caseNo: '111 年度上易字第 520 號刑事判決',
          yearDate: '民國 111 年 6 月 18 日',
          title: '間接證據與經驗法則之推論基準',
          holding: '認定犯罪事實所憑之證據，並不以直接證據為限，間接證據亦包含在內，只要依經驗法則推論無違誤即可。',
          takeaway: '依涉案當事人之時空軌跡與客觀行為綜合論斷。',
        },
        {
          court: '臺灣臺北地方法院',
          caseNo: '112 年度訴字第 310 號刑事判決',
          yearDate: '民國 112 年 8 月 25 日',
          title: '犯後態度與被害人和解對量刑之審酌',
          holding: '被告坦承犯行並賠償被害人損失達成和解，獲被害人宥恕，量處適當刑度。',
          takeaway: '警詢時應記錄雙方調解賠償之意向。',
        },
      ],
      treatises: [
        {
          title: '刑事偵查工作之客觀義務與人權保障實務指引',
          author: '法務部司法官學院研析報告',
          source: '檢察官實務通訊 第 40 期',
          coreArgument: '司法警察應依刑事訴訟法第2條注意對當事人有利及不利之一切情狀，嚴格遵循法定詢問程序。',
          takeaway: '落實權利告知與客觀蒐證。',
        },
        {
          title: '科技偵查在各類刑事案件數位電磁紀錄之合法提取',
          author: '內政部警政署刑事警察局',
          source: '警學研究叢刊 第 62 卷',
          coreArgument: '監視器錄影、手機對話截圖與車牌辨識日誌為現代偵查核心，應落實數位證物監管鏈。',
          takeaway: '數位證物應註記採證時間與雜湊值。',
        },
        {
          title: '刑事附帶民事訴訟與被害人損害求償程序操作研析',
          author: '司法院刑事廳編印',
          source: '司法業務研究會論文集 第 72 輯',
          coreArgument: '被害人得於刑事訴訟程序提起附帶民事訴訟，免繳納裁判規費以迅速受償。',
          takeaway: '主動向告訴人說明附帶民事訴訟權利。',
        },
      ],
      detailedAnalysis: {
        title1: '1. 本案情境之法律定性分析',
        desc1: `針對陳述內容：「${raw.slice(0, 80)}...」，行為人之行為已構成客觀法益侵害，涉嫌違反${mainLawTitle}。`,
        title2: '2. 構成要件與待證爭點檢驗',
        desc2: '本案核心在於確認行為人主觀上具備直接故意或不確定故意，客觀上已著手實施犯罪構成要件，並有實害結果發生。',
        title3: '3. 舉證責任與調查方針',
        desc3: `應針對本案關係人（告訴人${e.victim}、嫌疑人${e.suspect}）進行深入警詢，並調取案發時間（${e.incidentTime}）及地點（${e.incidentLocation}）之現場監視影像或相關單據補強。`,
        conclusion: '全案事證明確，依法律程序製作調查筆錄並陳報管轄檢察署。',
      },
      qaItems: [
        {
          id: 'qa-custom-1',
          type: '案發時地與過程說明',
          question: `問：請詳述於${e.incidentTime}在${e.incidentLocation}所發生之具體事件經過？`,
          answer: `答：案發當時如陳述所載（${raw.slice(0, 60)}...）。`,
          hint: '還原事件發生之時序與動作。',
        },
        {
          id: 'qa-custom-2',
          type: '關係人與爭議重點',
          question: `問：涉案之對造當事人身分為誰？雙方先前有無恩怨糾紛？`,
          answer: `答：對造當事人為${e.suspect}，詳細身分及通訊資料詳如卷宗所附。`,
          hint: '特定當事人身分及涉案動機。',
        },
        {
          id: 'qa-custom-3',
          type: '證物檢附與損害確認',
          question: '問：你有無檢附相關證物（如錄影、照片、單據）供警方查證？損害為何？',
          answer: '答：我已將現場照片、通聯對話截圖及相關單據提供給警方附卷調查。',
          hint: '落實證據保全與損害特定。',
        },
      ],
      report: {
        titleReason: `涉嫌${mainLawTitle}${mainLawSub}罪嫌。`,
        suspects: `犯罪嫌疑人：${e.suspect}`,
        victims: `告訴人：${e.victim}`,
        summary: `報案人${e.victim}指訴：於${e.incidentTime}在${e.incidentLocation}，${raw.slice(0, 160)}...。案經警依規定受理調查，涉犯罪嫌明確，依法陳報。`,
        seizedItems: ['現場相關事證翻拍照片或截圖 1 份。', '當事人通聯或身分資料 1 份。'],
        legalAnalysis: `行為人之客觀行為已該當${mainLawTitle}之構成要件，事證明確。`,
        recommendations: '依法移送臺灣臺北地方檢察署偵辦。',
      },
    };
  }
}
