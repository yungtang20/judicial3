"""Create the initial 15 human-readable family question sources.

This is a deterministic bootstrap tool. The generated Markdown files become
the editable source of truth; runtime never imports this module.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "question_sources"

FAMILY_AXES = {
    "human_violence": [
        ("event_sequence", "context", "請依時間順序說明衝突或事件從開始到結束的經過。"),
        ("conduct_method", "conduct", "請說明各人做了哪些動作，以及使用了哪些物品或工具。"),
        ("body_area_frequency", "conduct", "請說明身體接觸的部位、次數、力道及持續時間。"),
        ("injury_result", "result", "請說明受傷、身體變化、就醫及診斷情形。"),
        ("intent_and_awareness", "mental_state", "請說明事件當時各人說了什麼，以及你如何理解其目的。"),
        ("evidence_and_causation", "evidence", "有哪些影像、診斷、物品、證人或其他資料可核對行為與結果？"),
        ("cessation_reason", "distinguishing", "相關行為因何停止，停止前後各人做了什麼？"),
        ("defense_or_necessity", "justification", "請說明事件中為保護自己、他人或避免危險而採取行動的具體情形？"),
        ("negligence_precautions", "mental_state", "若結果並非刻意造成，請說明當時實際採取哪些注意或避免措施？"),
        ("domestic_child_context", "procedure", "各參與者之間有何家庭、同住、照顧或兒少關係？"),
        ("immediate_safety_need", "procedure", "當事人目前需要哪些立即安全協助？")],
    "coercion_liberty_threat": [
        ("event_sequence", "context", "請依時間順序說明言語、動作及你後續反應的完整經過。"),
        ("force_or_threat", "conduct", "對方使用哪些言語、動作、物品或其他方式？"),
        ("content_and_demand", "conduct", "對方表達什麼內容，並要求你做或不做什麼？"),
        ("freedom_effect", "result", "你當時可以離開、拒絕或自行決定嗎？請說明具體情形。"),
        ("frequency_duration", "context", "相關行為發生幾次、持續多久，各次間有何關聯？"),
        ("evidence_sources", "evidence", "有哪些訊息、錄音、影像、定位、證人或其他資料可核對？"),
        ("movement_and_exit", "result", "當事人可活動的範圍、離開方式及受到阻礙的具體情形為何？"),
        ("property_transfer", "distinguishing", "請說明事件中財物被取走或交付的具體經過？"),
        ("property_transfer_context", "distinguishing", "財物移轉前後發生哪些言語或動作？"),
        ("stalking_pattern", "context", "各次接近、跟隨、聯絡或守候的時間、場所、方式及間隔為何？"),
        ("existing_protection", "procedure", "目前已有告誡、保護令或其他安全措施的情形為何？"),
        ("immediate_safety_need", "procedure", "當事人目前需要哪些立即安全協助？")],
    "property_possession_taking": [
        ("property_identity", "object", "涉及哪些財物？請說明名稱、數量、特徵、價值及辨識資料。"),
        ("possession_control", "relationship", "事件前由誰實際持有、保管、使用或控制財物？"),
        ("acquisition_method", "conduct", "財物如何被接觸、移動、取得或交付？"),
        ("authorization_scope", "authorization", "請說明是否有人同意接觸、保管、使用、攜出或處分，以及同意的範圍。"),
        ("lost_property_boundary", "distinguishing", "財物離開原持有人視線後，原持有人是否仍能掌握位置或立即取回？"),
        ("disposition_and_evidence", "evidence", "財物後續由誰控制、如何處理，有哪些影像、交易或權源資料？"),
        ("lawful_possession_origin", "distinguishing", "取得財物前是否因借用、保管、委託、職務或拾得而先合法持有？"),
        ("return_demand_response", "conduct", "何時以何方式要求返還或停止使用，對方如何回應及處理？"),
        ("aggravating_method", "conduct", "取得財物時是否涉及侵入、破壞安全設備、工具、多人分工或其他特殊方式？"),
        ("force_timing_degree", "distinguishing", "若有人受到強暴或脅迫，發生在取物前、中或後，對其反抗或決定造成何種影響？")],
    "property_damage": [
        ("property_identity", "object", "請說明受影響的物品、文書、建物或設施，以及持有或管理的人。"),
        ("condition_before", "context", "事件前該物品的外觀、功能及使用狀態如何？"),
        ("damage_method", "conduct", "物品如何被破壞、損壞、遮蔽或改變效用？"),
        ("damage_result", "result", "事件後有哪些外觀、功能或使用上的差異？"),
        ("authorization_or_reason", "authorization", "是否有人同意相關處理，或對物品權利存有爭議？"),
        ("repair_and_evidence", "evidence", "有哪些照片、估價、修繕、購買、證人或其他資料可核對？"),
        ("function_impairment", "result", "物品受影響的功能與持續時間為何？"),
        ("conduct_intent", "mental_state", "處理物品前後說了什麼、做了什麼，可反映當時如何理解行為結果？"),
        ("public_or_shared_property", "relationship", "物品是否為共有、公用、承租、受託管理或由多人共同使用？"),
        ("complaint_relationship", "procedure", "雙方是否具有親屬、同財共居或其他可能影響告訴程序的關係？")],
    "deception_disposition_trust": [
        ("representation", "conduct", "對方以何種方式表達哪些具體內容？"),
        ("truth_check", "evidence", "哪些內容可以由文件、紀錄或其他人確認真實性？"),
        ("knowledge_timeline", "mental_state", "各方在何時知道哪些資訊，資訊來源為何？"),
        ("property_disposition", "conduct", "誰因何原因交付財物、匯款、簽約或作成其他處分？"),
        ("entrustment_duty", "relationship", "雙方有何委託、職務、契約或信賴關係，約定內容為何？"),
        ("loss_money_flow", "result", "財產如何流動、目前去向與損失如何，有哪些金流或通訊資料？"),
        ("reliance_causation", "causation", "作成財產處分前實際相信哪些內容，若未接收到該內容是否仍會處分？"),
        ("benefit_recipient", "result", "財產利益最後由誰取得、控制或使用，與各參與者有何關係？"),
        ("duty_violation", "conduct", "受託或任職者原應如何處理事務，實際處理與約定有何差異？"),
        ("multiple_victims_pattern", "evidence", "是否有其他相同說法、帳戶、聯絡方式或交易模式可供交叉核對？")],
    "document_seal_identity": [
        ("document_type", "object", "涉及何種文書、印文、署名、帳號或身分資料？"),
        ("nominal_person", "relationship", "文件或標示所呈現的名義人是誰，實際製作或使用者是誰？"),
        ("creation_process", "conduct", "內容、署名、印文或電子紀錄如何製作或變更？"),
        ("authorization", "authorization", "請說明名義人是否同意製作、修改或使用，以及同意的範圍。"),
        ("use_target_purpose", "conduct", "該資料曾向誰提出、傳送或使用，目的及時間為何？"),
        ("harm_and_original", "evidence", "原始檔、版本紀錄、設備及可能受影響的人或權利為何？"),
        ("public_private_character", "distinguishing", "文件由何人依何職務或權限製作，原本用於證明何種事項？"),
        ("false_entry_source", "conduct", "不一致內容由誰提供、輸入、核對或核准，各階段如何進行？"),
        ("seal_signature_method", "conduct", "署名、印章、印文或電子簽章如何取得、製作及附加？"),
        ("copy_original_chain", "evidence", "正本、副本、掃描檔及各版本目前何在，如何確認製作時間與來源？")],
    "reputation_speech": [
        ("statement_content", "conduct", "請完整說明或保存相關文字、言語、影像及前後文。"),
        ("speaker_identity", "identity", "請說明內容由誰製作、發表、轉傳或管理，以及確認方式。"),
        ("audience_publicity", "context", "哪些人可以看到或聽到，實際傳達範圍為何？"),
        ("fact_or_opinion", "distinguishing", "請說明內容是在描述可查證的具體事情或表達評價與感受，以及判斷依據。"),
        ("purpose_and_basis", "mental_state", "發表者當時掌握哪些資料，為何發表或轉傳？"),
        ("platform_evidence_harm", "evidence", "有哪些截圖、網址、帳號、時間紀錄、證人及具體影響可核對？"),
        ("truth_verification", "evidence", "涉及具體事實時，發表前後曾以何種資料或方法查證？"),
        ("public_interest_context", "context", "內容涉及何種公共事務、個人爭議或其他目的，與受眾有何關聯？"),
        ("republication_edits", "conduct", "轉傳或再次發表時是否增刪內容、加入評語或改變可見範圍？"),
        ("removal_correction", "result", "內容後續被刪除、更正、道歉或繼續流傳的情形為何？")],
    "privacy_secret_sexual_image": [
        ("private_activity_or_data", "object", "涉及哪些活動、談話、資料、影像或聲音？"),
        ("expectation_context", "context", "當時場所、設備、遮蔽及對他人接觸的預期為何？"),
        ("capture_acquisition", "conduct", "資料或影像如何被觀看、拍攝、錄製、取得或保存？"),
        ("consent_scope", "authorization", "請說明是否曾同意觀看、拍攝、保存、傳送或公開，以及各自範圍。"),
        ("distribution_scope", "result", "資料曾傳給誰、放在哪裡、持續多久，是否仍可存取？"),
        ("device_and_preservation", "evidence", "涉及哪些帳號、裝置、檔案、連結、平台紀錄及保存方式？"),
        ("sexual_image_context", "distinguishing", "影像內容、拍攝情境及可辨識當事人的方式為何？"),
        ("deletion_and_copy", "result", "原始檔與複本目前位於何處，曾否刪除、備份或再次下載？"),
        ("profit_or_exchange", "mental_state", "取得或散布資料是否涉及金錢、交換、要求或其他利益？"),
        ("access_control", "evidence", "裝置、帳號、雲端或群組有哪些密碼、權限及存取紀錄可核對？")],
    "public_danger_traffic": [
        ("vehicle_route", "context", "請說明交通工具、駕駛人、行駛路線及時間地點。"),
        ("substance_use", "conduct", "請說明駕駛前是否飲用、服用或施用物質，以及種類、時間、數量及來源。"),
        ("driving_state", "result", "駕駛時的意識、反應、視線、平衡及操作狀況如何？"),
        ("test_procedure", "evidence", "何時、何地、以何方式檢測，結果、單位及文件為何？"),
        ("collision_awareness", "mental_state", "若有事故，駕駛人何時如何察覺碰撞或人員可能受傷？"),
        ("post_accident_action", "conduct", "事故後有哪些停車、查看、救助、報警、留資料或離場行為？"),
        ("operation_actual_control", "distinguishing", "交通工具是否啟動或移動，由誰控制方向、動力及煞車？"),
        ("external_factors", "context", "當時道路、天候、照明、車況、疾病或疲勞等因素為何？"),
        ("injury_causation", "causation", "碰撞、倒地、傷勢、送醫及後續變化的時間順序為何？"),
        ("prior_case_status", "evidence", "若涉及前案，行為日、處分、判決及確定日期可由哪些正式資料確認？")],
    "drugs_firearms_organization": [
        ("item_identity", "object", "請說明涉及的物質、藥品、器械、零件或其他物品，以及外觀、數量及包裝。"),
        ("possession_location", "conduct", "物品在何處、由誰實際控制，如何取得或移動？"),
        ("source_upstream", "relationship", "物品來源為何，如何聯繫、約定及交付？"),
        ("destination_downstream", "relationship", "物品預定或實際交給何人，以何方式處理？"),
        ("purpose_knowledge", "mental_state", "請說明各人如何理解物品性質及處理目的，以及判斷依據。"),
        ("money_communication_evidence", "evidence", "有哪些鑑驗、金流、通訊、定位、包裝或指紋資料可核對？"),
        ("manufacture_transport_sale", "conduct", "是否涉及製造、運輸、販賣、轉讓或分裝，各人具體分工為何？"),
        ("organization_structure", "relationship", "參與者如何聯繫、決策、分工、分配利益及持續運作？"),
        ("item_function_test", "evidence", "物品功能、成分、純度、殺傷力或管制屬性由何種鑑驗確認？"),
        ("lawful_authority", "authorization", "是否有處方、許可、執照、職務或其他合法持有使用依據？")],
    "justice_public_service_order": [
        ("official_or_proceeding", "context", "涉及何種公務、司法程序、投票、秩序維護或證據處理？"),
        ("actor_role", "identity", "各參與者的身分、職務、程序角色及當時任務為何？"),
        ("event_sequence", "context", "請依時間順序說明通知、指示、陳述、行為及處理結果。"),
        ("statement_or_method", "conduct", "具體說了什麼、做了什麼，使用哪些物品或方式？"),
        ("knowledge_authority", "mental_state", "各人當時知道哪些職務、命令、程序或證據狀態？"),
        ("effect_and_record", "evidence", "對程序或職務造成何種影響，有哪些公文、錄音、影像或證人？"),
        ("lawfulness_notice", "distinguishing", "命令、職務或程序的內容如何告知，各人當時如何理解其依據？"),
        ("evidence_identity_chain", "evidence", "涉及的證物或資料如何識別、保管、移動、變更或滅失？"),
        ("statement_truth_basis", "evidence", "相關陳述涉及哪些具體事實，陳述人當時的知識來源為何？"),
        ("escape_concealment", "conduct", "若涉及脫逃或藏匿，原受何種拘束、如何離開或獲得協助？")],
    "computer_network_digital_evidence": [
        ("account_device", "object", "涉及哪些帳號、裝置、系統、IP、網域或資料？"),
        ("authorization_scope", "authorization", "請說明各人的存取、操作或管理權限，以及權限取得方式。"),
        ("access_path", "conduct", "系統或資料如何被登入、存取、輸入指令或使用？"),
        ("data_system_change", "result", "哪些資料或系統狀態被新增、變更、刪除或妨礙？"),
        ("identity_attribution", "evidence", "帳號、IP 或裝置如何連結到特定使用者，有何替代可能？"),
        ("logs_preservation", "evidence", "有哪些日誌、映像、封包、平台紀錄及保全程序可核對？"),
        ("credential_source", "conduct", "帳號、密碼、憑證、權杖或其他登入資料如何取得及使用？"),
        ("time_sync", "evidence", "各裝置與系統時間如何校準，日誌時區及時間誤差為何？"),
        ("malware_or_tool", "object", "是否使用程式、指令、惡意程式或其他工具，其來源與功能為何？"),
        ("business_impact_recovery", "result", "系統受影響的範圍、持續時間、復原方式及相關成本為何？")],
    "sexual_child_exploitation": [
        ("relationship_power", "relationship", "雙方的年齡、關係、照顧、職務或權力差異為何？"),
        ("event_sequence", "context", "請依當事人能承受的方式，按時間說明事件前後經過。"),
        ("conduct_description", "conduct", "發生哪些言語、接觸、拍攝、招募、控制或利益交換行為？"),
        ("consent_capacity", "authorization", "當事人如何表達意願，當時身心、年齡及理解狀況為何？"),
        ("force_dependency", "context", "是否涉及暴力、威脅、酒藥、依賴、經濟或其他影響選擇的情形？"),
        ("safety_special_evidence", "evidence", "目前安全需求及可保存的醫療、數位、場所或證人資料為何？"),
        ("age_identity_proof", "evidence", "當事人年齡及身分可由哪些正式資料確認？"),
        ("communication_after_event", "evidence", "事件後有哪些聯絡、道歉、要求、威脅、刪除或保留資料的情形？"),
        ("exploitation_benefit", "result", "是否涉及招募、仲介、報酬、交換或他人獲利，具體流向為何？"),
        ("special_interview_needs", "procedure", "當事人目前需要何種陪同、隔離、翻譯、醫療或其他程序協助？")],
    "money_flow_laundering_stolen_goods": [
        ("asset_origin", "object", "涉及哪些款項、虛擬資產或物品，其最初來源為何？"),
        ("account_control", "relationship", "涉及哪些帳戶、錢包或收受者，由誰申請、持有及實際控制？"),
        ("transfer_timeline", "conduct", "請依時間列出每筆收受、轉出、提領、兌換或交付。"),
        ("instruction_contact", "relationship", "誰指示或協助處理，如何聯絡及約定報酬？"),
        ("knowledge_red_flags", "mental_state", "處理前後知道哪些來源、用途或異常情形？"),
        ("records_destination", "evidence", "有哪些交易明細、設備、通訊、監視器及最終去向可核對？"),
        ("layering_conversion", "conduct", "款項或資產是否經過多層轉帳、提領、兌換、購買或跨境移動？"),
        ("property_crime_link", "evidence", "資產與前置犯罪或特定被害來源間有哪些可核對連結？"),
        ("consideration_price", "distinguishing", "收受物品或資產時支付何種對價，價格與通常交易有何差異？"),
        ("return_report_freeze", "result", "發現異常後是否返還、通報、停止交易或配合圈存，時間與結果為何？")],
    "specialist_routes": [
        ("route_identification", "context", "本案涉及哪一種特別制度、物品、職務或受保護利益？"),
        ("actor_qualification", "identity", "各行為人的身分、資格、職務或特殊關係為何？"),
        ("object_identity", "object", "涉及的文件、貨幣、證券、器具、場所或其他客體為何？"),
        ("conduct_sequence", "conduct", "請依時間順序說明具體行為及各人分工。"),
        ("authority_purpose", "mental_state", "請說明是否有授權、職務依據或其他目的，以及相關資料。"),
        ("specialist_evidence", "evidence", "有哪些主管機關資料、鑑定、公文、紀錄或證人可核對？"),
        ("special_law_status", "evidence", "行為時適用的特別法版本、許可或主管機關認定可由何處確認？"),
        ("quantity_standard", "object", "涉及的數量、面額、規格、度量或法定標準如何測量及確認？"),
        ("public_effect", "result", "行為對國家、公務、選舉、交易秩序或其他保護利益造成何種具體影響？"),
        ("referral_need", "procedure", "哪些事項需要主管機關、專責單位、檢察官或鑑定機關進一步確認？")],
}

GENERIC_ELEMENT_AXES = {
    "mental_state": ("element_mental_state", "請說明各參與者在事件前後知道哪些情況，以及其理解與目的？"),
    "object": ("element_object", "本案涉及哪些人、物品、資料、權利或場所？"),
    "relationship": ("element_relationship", "各參與者之間具有何種身分、持有、職務或其他關係？"),
    "result": ("element_result", "相關行為造成哪些實際結果或後續變化？"),
    "authorization": ("element_authorization", "相關行為有何同意、授權、許可或職務依據？"),
}

FAMILY_ELEMENT_COMPLEMENTS = {
    "coercion_liberty_threat": ("mental_state", "object", "relationship"),
    "computer_network_digital_evidence": ("mental_state",),
    "deception_disposition_trust": ("object",),
    "document_seal_identity": ("mental_state", "result"),
    "drugs_firearms_organization": ("result",),
    "human_violence": ("object", "relationship"),
    "justice_public_service_order": ("object", "relationship", "result"),
    "privacy_secret_sexual_image": ("relationship",),
    "property_possession_taking": ("mental_state", "result"),
    "reputation_speech": ("relationship",),
    "sexual_child_exploitation": ("mental_state", "object"),
    "specialist_routes": ("authorization", "relationship"),
}

for family_id, element_types in FAMILY_ELEMENT_COMPLEMENTS.items():
    for element_type in element_types:
        fact_target, text = GENERIC_ELEMENT_AXES[element_type]
        FAMILY_AXES[family_id].append((fact_target, element_type, text))

ROLE_TEXT = {
    "victim": lambda text: text,
    "suspect": lambda text: text.replace("對方", "你或其他人").replace("你當時可以", "當事人當時是否可以"),
    "witness": lambda text: "就你親自看見、聽見或處理的部分，" + text,
}

PREFIXES = ["HV","CT","PT","PD","DF","DS","RS","PS","TR","DO","JO","CN","SC","MF","SP"]


def render_family(entry: dict, prefix: str) -> str:
    family_id = entry["family_id"]
    axes = FAMILY_AXES[family_id]
    lines = [
        f"# {entry['label']}家族問句主檔",
        "",
        "## Metadata",
        "",
        f"- family_id: `{family_id}`",
        "- version: `1.0.0`",
        "- editorial_status: `AI_REVIEWED`",
        "- method_review_status: `AI_REVIEWED`",
        "- legal_review_status: `HUMAN_REVIEW_REQUIRED`",
        "- runtime_status: `AVAILABLE_WITH_WARNING`",
        "- disclaimer: `DRAFT / NOT LEGALLY APPROVED`",
        "",
        "## Route scope",
        "",
        f"- included_parent_routes: `{','.join(entry['routes'])}`",
        "- excluded_routes: 未列入者不得由本家族自行推定。",
        "",
        "## Questions",
        "",
        "| question_id | role | text | fact_target | element_type | layer | requirement | routes | preconditions | prohibitions | source | version | editorial_status | method_review_status | legal_review_status | runtime_status | page_cost | template_binding |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    routes = ",".join(entry["routes"])
    for role_index, role in enumerate(("victim", "suspect", "witness")):
        role_code = ("V", "S", "W")[role_index]
        for index, (target, element, text) in enumerate(axes, start=1):
            layer = "family_skeleton" if index <= 4 else "element_supplement"
            requirement = "REQUIRED" if index <= 6 else "CONDITIONAL"
            qid = f"{prefix}-{role_code}{index:02d}"
            role_text = ROLE_TEXT[role](text)
            lines.append(
                f"| {qid} | {role} | {role_text} | {target} | {element} | {layer} | {requirement} | {routes} | NONE | LEADING,ASSUMES_GUILT | INTERNAL_FAMILY_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |"
            )
    lines.extend([
        "",
        "## Conditional modules",
        "",
        "- 僅在前置事實成立時加入補強題；不得因候選分數自動預設事實。",
        "",
        "## Element gap matrix",
        "",
    ])
    for index, (target, _element, _text) in enumerate(axes, start=1):
        lines.append(f"- `{target}`: `{prefix}-V{index:02d}`, `{prefix}-S{index:02d}`, `{prefix}-W{index:02d}`")
    lines.extend([
        "",
        "## Review boundary",
        "",
        "- 本檔可供系統顯示及工程測試，但不代表法律核准。",
        "- 法律來源、行為時法及機關內規未逐題完成人工核對者，狀態維持 `HUMAN_REVIEW_REQUIRED`。",
        "",
    ])
    return "\n".join(lines)


def render_common() -> str:
    rows = [
        ("C-V01","victim","請說明你與本案及其他關係人的關係。","identity","identity","procedure","REQUIRED"),
        ("C-V02","victim","請依時間順序，從你認為最早相關的事情開始完整說明。","free_narrative","context","procedure","REQUIRED"),
        ("C-V03","victim","哪些內容是你親自知道，哪些是他人告知或事後推測？","knowledge_basis","evidence","procedure","REQUIRED"),
        ("C-V04","victim","你有哪些資料、物品或證人可以提供警方查證？","evidence","evidence","procedure","REQUIRED"),
        ("C-V05","victim","你是否還有需要補充、更正或提出告訴意願的事項？","closing","procedure","procedure","REQUIRED"),
        ("C-S01","suspect","警方已向你告知本次詢問的案由及相關權利，你是否了解？","rights_notice","procedure","procedure","REQUIRED"),
        ("C-S02","suspect","請依時間順序，從你認為最早相關的事情開始完整說明。","free_narrative","context","procedure","REQUIRED"),
        ("C-S03","suspect","對於目前所述事情，你有哪些不同說明或需要釐清之處？","response","context","procedure","REQUIRED"),
        ("C-S04","suspect","你有哪些對自己有利的事實或證據希望警方調查？","exculpatory_evidence","evidence","procedure","REQUIRED"),
        ("C-S05","suspect","你是否還有需要補充或更正的事項？","closing","procedure","procedure","REQUIRED"),
        ("C-W01","witness","請說明你與本案各關係人的關係，以及你當時所在位置。","witness_basis","identity","procedure","REQUIRED"),
        ("C-W02","witness","請依時間順序說明你親自看見、聽見或處理的經過。","free_narrative","context","procedure","REQUIRED"),
        ("C-W03","witness","請說明哪些內容不是你親自得知，以及其來源。","hearsay_source","evidence","procedure","REQUIRED"),
        ("C-W04","witness","你有哪些資料或其他證人線索可以提供查證？","evidence","evidence","procedure","REQUIRED"),
        ("C-W05","witness","你是否還有需要補充或更正的事項？","closing","procedure","procedure","REQUIRED"),
    ]
    lines = ["# 通用程序問句主檔","","## Metadata","","- family_id: `common_procedure`","- version: `1.0.0`","- legal_review_status: `HUMAN_REVIEW_REQUIRED`","- runtime_status: `AVAILABLE_WITH_WARNING`","","## Questions","","| question_id | role | text | fact_target | element_type | layer | requirement | routes | preconditions | prohibitions | source | version | editorial_status | method_review_status | legal_review_status | runtime_status | page_cost | template_binding |","|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for qid, role, text, target, element, layer, requirement in rows:
        lines.append(f"| {qid} | {role} | {text} | {target} | {element} | {layer} | {requirement} | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |")
    lines.extend(["","## Review boundary","","- 權利告知與程序文字必須再與現行法及機關內規核對。",""])
    return "\n".join(lines)


def render_modules() -> str:
    rows = [
        ("M-DV-V01", "victim", "請說明你與對方的家庭、同住、照顧或親密關係？", "domestic_relationship", "relationship", "DOMESTIC_RELATIONSHIP_CONFIRMED"),
        ("M-DV-S01", "suspect", "請說明你與對方的家庭、同住、照顧或親密關係？", "domestic_relationship", "relationship", "DOMESTIC_RELATIONSHIP_CONFIRMED"),
        ("M-DV-W01", "witness", "就你親自知道的部分，雙方有何家庭、同住、照顧或親密關係？", "domestic_relationship", "relationship", "DOMESTIC_RELATIONSHIP_CONFIRMED"),
        ("M-DV-V02", "victim", "你目前需要哪些立即安全協助？", "immediate_safety_need", "procedure", "DOMESTIC_RELATIONSHIP_CONFIRMED"),
        ("M-JU-S01", "suspect", "你的出生年月日可由哪些資料確認？", "minor_age_proof", "identity", "MINOR_INVOLVED_CONFIRMED"),
        ("M-JU-W01", "witness", "未成年當事人的年齡可由哪些資料確認？", "minor_age_proof", "identity", "MINOR_INVOLVED_CONFIRMED"),
        ("M-JU-S02", "suspect", "你目前需要法定代理人、陪同人或其他程序協助嗎？", "minor_procedure_support", "procedure", "MINOR_INVOLVED_CONFIRMED"),
        ("M-CP-V01", "victim", "你目前有何照顧、安置、醫療或安全協助需求？", "child_safety_support", "procedure", "MINOR_INVOLVED_CONFIRMED"),
        ("M-SX-V01", "victim", "你希望由何種性別或具何種專業的人員進行後續詢問？", "special_interview_preference", "procedure", "SEXUAL_CASE_ROUTE"),
        ("M-SX-V02", "victim", "你目前需要哪些陪同、醫療、隔離或其他程序協助？", "special_interview_support", "procedure", "SEXUAL_CASE_ROUTE"),
        ("M-ST-V01", "victim", "目前已有告誡、保護令或其他安全措施的情形為何？", "existing_protection", "procedure", "STALKING_ROUTE"),
        ("M-ST-V02", "victim", "哪些近期變化使你認為風險增加或降低？", "risk_change", "context", "STALKING_ROUTE"),
        ("M-IN-V01", "victim", "你慣用何種語言或溝通方式？", "communication_language", "procedure", "INTERPRETER_NEED_CONFIRMED"),
        ("M-IN-S01", "suspect", "你慣用何種語言或溝通方式？", "communication_language", "procedure", "INTERPRETER_NEED_CONFIRMED"),
        ("M-IN-W01", "witness", "你慣用何種語言或溝通方式？", "communication_language", "procedure", "INTERPRETER_NEED_CONFIRMED"),
        ("M-IN-V02", "victim", "你需要何種翻譯、手語或其他溝通協助？", "communication_support", "procedure", "INTERPRETER_NEED_CONFIRMED"),
        ("M-IN-S02", "suspect", "你需要何種翻譯、手語或其他溝通協助？", "communication_support", "procedure", "INTERPRETER_NEED_CONFIRMED"),
        ("M-NI-S01", "suspect", "請說明本次在夜間進行詢問的原因？", "night_interview_reason", "procedure", "NIGHT_INTERVIEW_CONFIRMED"),
        ("M-NI-S02", "suspect", "你目前的身心狀況是否適合繼續接受詢問？", "interview_fitness", "procedure", "NIGHT_INTERVIEW_CONFIRMED"),
        ("M-RC-V01", "victim", "錄音或錄影中斷發生在何時？", "recording_interruption_time", "procedure", "RECORDING_INTERRUPTION_CONFIRMED"),
        ("M-RC-S01", "suspect", "錄音或錄影中斷發生在何時？", "recording_interruption_time", "procedure", "RECORDING_INTERRUPTION_CONFIRMED"),
        ("M-RC-W01", "witness", "錄音或錄影中斷發生在何時？", "recording_interruption_time", "procedure", "RECORDING_INTERRUPTION_CONFIRMED"),
        ("M-RC-S02", "suspect", "錄音或錄影中斷的原因為何？", "recording_interruption_reason", "procedure", "RECORDING_INTERRUPTION_CONFIRMED"),
        ("M-ID-V01", "victim", "請確認本案使用的代號及其對應紀錄由何處查得？", "coded_identity_record", "evidence", "CODED_VICTIM_CONFIRMED"),
        ("M-GE-V01", "victim", "事件發生時雙方在工作或教育場所各自具有何種身分？", "work_education_role", "identity", "WORK_OR_EDUCATION_CONTEXT"),
        ("M-GE-S01", "suspect", "事件發生時雙方在工作或教育場所各自具有何種身分？", "work_education_role", "identity", "WORK_OR_EDUCATION_CONTEXT"),
        ("M-GE-W01", "witness", "就你親自知道的部分，雙方在工作或教育場所各自具有何種身分？", "work_education_role", "identity", "WORK_OR_EDUCATION_CONTEXT"),
        ("M-DI-S01", "suspect", "對於雙方陳述不一致的部分，請依你的記憶逐項說明事實與依據？", "role_statement_difference", "distinguishing", "ROLE_DISCREPANCY_PRESENT"),
    ]
    lines = ["# 條件式程序模組問句主檔", "", "## Metadata", "", "- family_id: `common_procedure`", "- version: `1.0.0`", "- legal_review_status: `HUMAN_REVIEW_REQUIRED`", "- runtime_status: `AVAILABLE_WITH_WARNING`", "", "## Questions", "", "| question_id | role | text | fact_target | element_type | layer | requirement | routes | preconditions | prohibitions | source | version | editorial_status | method_review_status | legal_review_status | runtime_status | page_cost | template_binding |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for qid, role, text, target, element, precondition in rows:
        lines.append(f"| {qid} | {role} | {text} | {target} | {element} | conditional_module | CONDITIONAL | ALL | {precondition} | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |")
    lines.extend(["", "## Activation boundary", "", "- 前置條件未由案件文字或候選 route 明確支持時不得顯示。", "- 程序模組仍須依現行法及機關內規完成人工核對。", ""])
    return "\n".join(lines)


def main() -> None:
    manifest = json.loads((SOURCE_ROOT / "families.manifest.json").read_text(encoding="utf-8"))
    family_dir = SOURCE_ROOT / "families"
    procedure_dir = SOURCE_ROOT / "procedure"
    family_dir.mkdir(parents=True, exist_ok=True)
    procedure_dir.mkdir(parents=True, exist_ok=True)
    for entry, prefix in zip(manifest["families"], PREFIXES, strict=True):
        target = SOURCE_ROOT / entry["file"]
        target.write_text(render_family(entry, prefix), encoding="utf-8", newline="\n")
    (procedure_dir / "common.md").write_text(render_common(), encoding="utf-8", newline="\n")
    (procedure_dir / "modules.md").write_text(render_modules(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
