"""
AxiomGH — CISD 2026 Data Seeding Script
Run with: python manage.py shell < seed_data.py
OR copy into Django shell line by line

Loads all 23 directive sections and ~180 questions into the database.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'axiomgh.settings')
django.setup()

from core.models import DirectiveSection, Question

print("🌱 Starting AxiomGH data seed...")

# Clear existing data
Question.objects.all().delete()
DirectiveSection.objects.all().delete()
print("✓ Cleared existing data")

# ── SECTIONS ──────────────────────────────────────────────────────────────────
SECTIONS = [
    {"number": "01", "title": "Board Governance",                  "weight": 9,  "risk_level": "critical", "directive_reference": "Part II, Para 5",    "order": 1},
    {"number": "02", "title": "Senior Management",                 "weight": 8,  "risk_level": "critical", "directive_reference": "Part II, Para 6",    "order": 2},
    {"number": "03", "title": "Internal Audit",                    "weight": 7,  "risk_level": "high",     "directive_reference": "Part II, Para 7",    "order": 3},
    {"number": "04", "title": "Chief Information Security Officer","weight": 7,  "risk_level": "critical", "directive_reference": "Part III, Para 8-10","order": 4},
    {"number": "05", "title": "Cyber Security Risk Policy",        "weight": 8,  "risk_level": "critical", "directive_reference": "Part IV, Para 11-13","order": 5},
    {"number": "06", "title": "Risk Assessment & Mitigation",      "weight": 7,  "risk_level": "critical", "directive_reference": "Part IV, Para 14-18","order": 6},
    {"number": "07", "title": "Asset Management",                  "weight": 5,  "risk_level": "high",     "directive_reference": "Part V, Para 19-22", "order": 7},
    {"number": "08", "title": "Cyber Defence Infrastructure",      "weight": 8,  "risk_level": "critical", "directive_reference": "Part VI, Para 23-41","order": 8},
    {"number": "09", "title": "Cyber Response & SIEM/SOC",         "weight": 7,  "risk_level": "critical", "directive_reference": "Part VII, Para 42-48","order": 9},
    {"number": "10", "title": "Employee Access to ICT Systems",    "weight": 5,  "risk_level": "high",     "directive_reference": "Part VIII, Para 49", "order": 10},
    {"number": "11", "title": "Electronic Banking Platforms",      "weight": 5,  "risk_level": "high",     "directive_reference": "Part X, Para 55-63", "order": 11},
    {"number": "12", "title": "Training, Awareness & Competence",  "weight": 4,  "risk_level": "medium",   "directive_reference": "Part XI, Para 64-68","order": 12},
    {"number": "13", "title": "External Connections",              "weight": 4,  "risk_level": "high",     "directive_reference": "Part XII, Para 69-74","order": 13},
    {"number": "14", "title": "Cloud Services",                    "weight": 4,  "risk_level": "high",     "directive_reference": "Part XIII, Para 75-79","order": 14},
    {"number": "15", "title": "Banks with International Affiliation","weight": 2, "risk_level": "medium",  "directive_reference": "Part XIV, Para 80-81","order": 15},
    {"number": "16", "title": "Physical Security",                 "weight": 3,  "risk_level": "medium",   "directive_reference": "Part XV, Para 82-85","order": 16},
    {"number": "17", "title": "Human Resource Management",         "weight": 3,  "risk_level": "medium",   "directive_reference": "Part XVI, Para 86-89","order": 17},
    {"number": "18", "title": "Contractual Requirements",          "weight": 2,  "risk_level": "medium",   "directive_reference": "Part XVII, Para 90", "order": 18},
    {"number": "19", "title": "ISMS & ISO 27001 Certification",    "weight": 4,  "risk_level": "high",     "directive_reference": "Part IV, Para 4(9)", "order": 19},
    {"number": "20", "title": "Business Continuity",               "weight": 4,  "risk_level": "high",     "directive_reference": "Part II, Para 5(4)", "order": 20},
    {"number": "21", "title": "Digital Innovations — AI & Blockchain","weight": 5,"risk_level": "high",   "directive_reference": "Part XVIII, Para 91","order": 21},
    {"number": "22", "title": "Data Centre Operations",            "weight": 6,  "risk_level": "high",     "directive_reference": "Part XIX, Para 92-104","order": 22},
    {"number": "23", "title": "API Security",                      "weight": 5,  "risk_level": "high",     "directive_reference": "Part VI, Para 38",   "order": 23},
]

# ── QUESTIONS ─────────────────────────────────────────────────────────────────
QUESTIONS = {
    "01": [
        {"number": "1.1",  "text": "Has the Board formally determined and documented the institution's cyber and information security risk management strategy?", "points": 10, "clause": "Para 5(1)"},
        {"number": "1.2",  "text": "Has the Board approved institutional policies covering cyber security, outsourcing, survivability, backup and recovery from cyber incidents?", "points": 10, "clause": "Para 5(2)"},
        {"number": "1.3",  "text": "Has the Board appointed a Board Sub-Committee on Cyber and Information Security with a well-defined charter?", "points": 10, "clause": "Para 5(3)"},
        {"number": "1.4",  "text": "Has the Board approved the annual work plan for cyber and information security, business continuity and disaster recovery?", "points": 8, "clause": "Para 5(4)"},
        {"number": "1.5",  "text": "Does the Board receive quarterly reports on all cyber and information security incidents?", "points": 8, "clause": "Para 5(5)"},
        {"number": "1.6",  "text": "Does the Board receive immediate reports on significant cyber and information security incidents?", "points": 10, "clause": "Para 5(6)"},
        {"number": "1.7",  "text": "Does the Board dedicate at least two meetings per year specifically to cyber and information security risks and countermeasures?", "points": 8, "clause": "Para 5(7)"},
        {"number": "1.8",  "text": "Does the Board hold an annual discussion on the adequacy of the institution's cyber and information security policies and strategies?", "points": 8, "clause": "Para 5(8)"},
        {"number": "1.9",  "text": "Does the Board formally approve all new products and services before launch, including assessment of associated cyber risks?", "points": 8, "clause": "Para 5(11)"},
        {"number": "1.10", "text": "Does the Board receive both quarterly reports on all incidents AND immediate reports on significant incidents as two separate reporting streams?", "points": 8, "clause": "Para 5(5-6)"},
    ],
    "02": [
        {"number": "2.1",  "text": "Has Senior Management created an institutional framework for cyber and information security risk management and oversees its implementation?", "points": 10, "clause": "Para 6(1)"},
        {"number": "2.2",  "text": "Has Senior Management formulated institutional policies about cyber security, outsourcing, survivability, backup and recovery?", "points": 8, "clause": "Para 6(2)"},
        {"number": "2.3",  "text": "Are cyber security policies reviewed at least once a year or when significant changes occur?", "points": 8, "clause": "Para 6(3)"},
        {"number": "2.4",  "text": "Does Senior Management hold meetings to review cyber security activities at least quarterly?", "points": 8, "clause": "Para 6(4)"},
        {"number": "2.5",  "text": "Does Senior Management receive quarterly and ad-hoc reports about cyber threats and countermeasures?", "points": 8, "clause": "Para 6(5)"},
        {"number": "2.6",  "text": "Does Senior Management review significant cyber incidents, analyse their implications, and report to the Board promptly?", "points": 10, "clause": "Para 6(6)"},
        {"number": "2.7",  "text": "Has Senior Management appointed a CISO as key management personnel responsible for information security?", "points": 10, "clause": "Para 6(8)"},
        {"number": "2.8",  "text": "Does Senior Management report all significant and suspected cyber incidents to the Bank of Ghana?", "points": 10, "clause": "Para 6(10)"},
        {"number": "2.9",  "text": "Does Senior Management conduct due diligence before appointing any ICT outsourcing service provider?", "points": 8, "clause": "Para 6(11)"},
        {"number": "2.10", "text": "Has a formal Cyber and Information Security Risk Committee been established with a well-defined charter, separate from the Board sub-committee?", "points": 10, "clause": "Para 6(7)"},
    ],
    "03": [
        {"number": "3.1", "text": "Is there an internal independent unit responsible for auditing cyber and information security?", "points": 10, "clause": "Para 7(1)"},
        {"number": "3.2", "text": "Has Senior Management allocated adequate resources and training for the cyber security audit function?", "points": 8, "clause": "Para 7(2)"},
        {"number": "3.3", "text": "Are all aspects of cyber security management audited at least once a year or per a risk-based audit approach?", "points": 10, "clause": "Para 7(3)"},
        {"number": "3.4", "text": "Does the annual audit review the institution's survivability, backup and recovery processes?", "points": 8, "clause": "Para 7(4)"},
        {"number": "3.5", "text": "Are audit findings on cyber security risks reported to both the Board and Senior Management?", "points": 10, "clause": "Para 7(5)"},
        {"number": "3.6", "text": "Is there a follow-up process for tracking cyber security audit issues with an escalation mechanism to Senior Management?", "points": 8, "clause": "Para 7(8)"},
    ],
    "04": [
        {"number": "4.1",  "text": "Has the Board appointed a qualified individual as CISO with prior written approval from the Bank of Ghana?", "points": 10, "clause": "Para 8(1)"},
        {"number": "4.2",  "text": "Is the CISO competent based on appropriate education, training and experience?", "points": 8, "clause": "Para 8(2)"},
        {"number": "4.3",  "text": "Does the CISO hold no other position that could create a conflict of interest with CISO responsibilities?", "points": 8, "clause": "Para 8(3)"},
        {"number": "4.4",  "text": "Does the CISO report directly to the Managing Director or Chief Executive Officer?", "points": 10, "clause": "Para 9(2)"},
        {"number": "4.5",  "text": "Does the CISO have a documented cyber security strategy and programme aligned with the institution's business strategy?", "points": 8, "clause": "Para 10(2)"},
        {"number": "4.6",  "text": "Does the CISO conduct cyber security readiness exercises at least quarterly for one or more institutional entities?", "points": 8, "clause": "Para 10(9a)"},
        {"number": "4.7",  "text": "Does the CISO conduct a full institution-wide cyber exercise at least once per year?", "points": 8, "clause": "Para 10(9b)"},
        {"number": "4.8",  "text": "Has the CISO formed a Cyber Incident Response Team?", "points": 10, "clause": "Para 10(13)"},
        {"number": "4.9",  "text": "Does the CISO develop and maintain metrics and indicators to assess the effectiveness of cyber security systems?", "points": 8, "clause": "Para 10(15)"},
        {"number": "4.10", "text": "Does the CISO continuously monitor cyber security trends and emerging attack techniques?", "points": 6, "clause": "Para 10(12)"},
        {"number": "4.11", "text": "Does the CISO promote cyber security awareness and train employees, suppliers, partners and customers?", "points": 6, "clause": "Para 10(11)"},
    ],
    "05": [
        {"number": "5.1", "text": "Has the institution developed a formal Cyber and Information Security Policy approved by the Board?", "points": 10, "clause": "Para 11"},
        {"number": "5.2", "text": "Does the policy cover all required areas including risk management, incident response, asset management and business continuity?", "points": 10, "clause": "Para 11"},
        {"number": "5.3", "text": "Are there documented procedures for implementing the cyber security policy across all institutional units?", "points": 8, "clause": "Para 12"},
        {"number": "5.4", "text": "Has a Cyber and Information Security Risk Management Committee been appointed with a well-defined charter?", "points": 10, "clause": "Para 13"},
        {"number": "5.5", "text": "Does the Risk Management Committee meet regularly and report findings to Senior Management and the Board?", "points": 8, "clause": "Para 13"},
        {"number": "5.6", "text": "Is the cyber security methodology compliant with international standards such as NIST and ISO?", "points": 8, "clause": "Para 4(11)"},
        {"number": "5.7", "text": "Is the institution ISO 27001 certified or actively working toward certification as required by the CISD?", "points": 10, "clause": "Para 4(9)"},
        {"number": "5.8", "text": "Where applicable, is the institution PCI-DSS certified for handling card payment data?", "points": 8, "clause": "Para 4(10)"},
    ],
    "06": [
        {"number": "6.1", "text": "Has the institution implemented a formal cyber security risk management framework covering identification, assessment, mitigation and monitoring?", "points": 10, "clause": "Para 14"},
        {"number": "6.2", "text": "Is there a documented risk identification process that systematically identifies cyber threats relevant to the institution's operations?", "points": 8, "clause": "Para 15"},
        {"number": "6.3", "text": "Are formal risk assessments conducted regularly and documented with risk ratings?", "points": 10, "clause": "Para 16"},
        {"number": "6.4", "text": "Are risk mitigation measures implemented and tracked for all identified high and critical risks?", "points": 10, "clause": "Para 17"},
        {"number": "6.5", "text": "Is there an ongoing risk monitoring process with regular reporting to Senior Management?", "points": 8, "clause": "Para 18"},
        {"number": "6.6", "text": "Does the institution document all cyber and information security risks relevant to its operations and the measures taken to mitigate them?", "points": 8, "clause": "Para 4(6)"},
        {"number": "6.7", "text": "Are cyber security scenarios assessed for their potential impact on customers, suppliers and service providers — not just the institution itself?", "points": 8, "clause": "Para 4(7)"},
        {"number": "6.8", "text": "Is residual risk formally accepted and documented by Senior Management after mitigation controls are applied?", "points": 8, "clause": "Para 10(6c)"},
    ],
    "07": [
        {"number": "7.1", "text": "Does the institution maintain a complete and up-to-date inventory of all ICT assets?", "points": 10, "clause": "Para 19"},
        {"number": "7.2", "text": "Is ownership assigned to all ICT assets with a designated responsible individual or team?", "points": 8, "clause": "Para 20"},
        {"number": "7.3", "text": "Is there an acceptable use policy for ICT assets that is communicated to all employees?", "points": 8, "clause": "Para 21"},
        {"number": "7.4", "text": "Are all assets classified by sensitivity and criticality with appropriate controls applied per classification?", "points": 10, "clause": "Para 22"},
        {"number": "7.5", "text": "Is there a process for tracking asset lifecycle from procurement through to disposal, including secure data destruction?", "points": 8, "clause": "Para 22"},
        {"number": "7.6", "text": "Are critical assets identified and subject to enhanced security controls and monitoring?", "points": 8, "clause": "Para 22"},
        {"number": "7.7", "text": "Is the asset inventory reviewed and updated at least annually or when significant changes occur?", "points": 6, "clause": "Para 19"},
    ],
    "08": [
        {"number": "8.1",  "text": "Is appropriate security infrastructure deployed including firewalls, intrusion detection/prevention systems, and endpoint protection?", "points": 10, "clause": "Para 23"},
        {"number": "8.2",  "text": "Has the institution implemented a documented security architecture aligned with its risk profile?", "points": 8, "clause": "Para 24"},
        {"number": "8.3",  "text": "Are network elements secured and monitored with access restricted to authorised personnel only?", "points": 8, "clause": "Para 25"},
        {"number": "8.4",  "text": "Is there a formal network management process including change management, monitoring and vulnerability patching?", "points": 8, "clause": "Para 26"},
        {"number": "8.5",  "text": "Is encryption applied to sensitive data both in transit and at rest?", "points": 10, "clause": "Para 27"},
        {"number": "8.6",  "text": "Is media encryption implemented for portable storage devices containing sensitive data?", "points": 8, "clause": "Para 28"},
        {"number": "8.7",  "text": "Is remote access to institutional systems controlled, monitored and subject to multi-factor authentication?", "points": 10, "clause": "Para 29"},
        {"number": "8.8",  "text": "Is internet access managed and filtered with controls to prevent access to malicious sites?", "points": 8, "clause": "Para 30"},
        {"number": "8.9",  "text": "Are web applications and websites protected against common attacks including OWASP Top 10 vulnerabilities?", "points": 8, "clause": "Para 31"},
        {"number": "8.10", "text": "Is access control and authentication implemented across all systems with least-privilege principles applied?", "points": 10, "clause": "Para 32"},
    ],
    "09": [
        {"number": "9.1", "text": "Is there a documented cyber response structure with clear hierarchy and responsibilities for incident management?", "points": 10, "clause": "Para 42"},
        {"number": "9.2", "text": "Is a Security Information and Event Management (SIEM) system deployed and actively monitored?", "points": 10, "clause": "Para 43"},
        {"number": "9.3", "text": "Is a Security Operations Centre (SOC) established, either in-house or through a managed service provider?", "points": 10, "clause": "Para 44"},
        {"number": "9.4", "text": "Is there a documented incident response methodology aligned with international standards?", "points": 8, "clause": "Para 45"},
        {"number": "9.5", "text": "Does the institution gather and act on cyber threat intelligence relevant to its operations?", "points": 8, "clause": "Para 46"},
        {"number": "9.6", "text": "Are all significant and suspected cyber incidents reported to the Bank of Ghana within required timeframes?", "points": 10, "clause": "Para 48"},
        {"number": "9.7", "text": "Is there a formal post-incident review process to identify lessons learned and implement improvements?", "points": 8, "clause": "Para 45"},
        {"number": "9.8", "text": "Are incident handling procedures documented and tested regularly?", "points": 8, "clause": "Para 47"},
    ],
    "10": [
        {"number": "10.1", "text": "Is access to ICT systems granted on a need-to-know, least-privilege basis with formal approval processes?", "points": 10, "clause": "Para 49"},
        {"number": "10.2", "text": "Are privileged accounts subject to enhanced controls including separate credentials and additional monitoring?", "points": 10, "clause": "Para 49"},
        {"number": "10.3", "text": "Are all user access rights reviewed at least quarterly and promptly revoked when no longer required?", "points": 10, "clause": "Para 49"},
        {"number": "10.4", "text": "Is multi-factor authentication enforced for access to critical systems and sensitive data?", "points": 10, "clause": "Para 49"},
        {"number": "10.5", "text": "Are BYOD (Bring Your Own Device) policies documented and enforced with appropriate technical controls?", "points": 8, "clause": "Para 53"},
        {"number": "10.6", "text": "Are institutional mobile devices managed through a Mobile Device Management (MDM) solution?", "points": 8, "clause": "Para 54"},
        {"number": "10.7", "text": "Is there a formal joiner-mover-leaver process ensuring access is updated promptly when staff change roles or leave?", "points": 10, "clause": "Para 49"},
        {"number": "10.8", "text": "Are all access control changes logged and regularly reviewed for anomalies?", "points": 8, "clause": "Para 49"},
    ],
    "11": [
        {"number": "11.1", "text": "Are all electronic banking platforms subject to formal security assessment before deployment?", "points": 10, "clause": "Para 55"},
        {"number": "11.2", "text": "Is strong customer authentication implemented for all electronic banking services?", "points": 10, "clause": "Para 57"},
        {"number": "11.3", "text": "Are institutional websites protected against common attacks and subject to regular security testing?", "points": 8, "clause": "Para 58"},
        {"number": "11.4", "text": "Are mobile banking applications developed and maintained in accordance with secure development standards?", "points": 8, "clause": "Para 59"},
        {"number": "11.5", "text": "Are customer security measures in place including fraud monitoring and transaction anomaly detection?", "points": 10, "clause": "Para 62"},
        {"number": "11.6", "text": "Is a formal password management policy in place covering complexity, expiry and storage requirements?", "points": 8, "clause": "Para 63"},
        {"number": "11.7", "text": "Are customers provided with security guidance and fraud awareness information for electronic banking services?", "points": 6, "clause": "Para 62"},
        {"number": "11.8", "text": "Are electronic banking platforms subject to regular penetration testing and vulnerability assessments?", "points": 8, "clause": "Para 55"},
        {"number": "11.9", "text": "Is there a process for monitoring and responding to electronic banking fraud in real time?", "points": 8, "clause": "Para 62"},
    ],
    "12": [
        {"number": "12.1", "text": "Have all staff in sensitive positions been identified and are they subject to enhanced security awareness training?", "points": 8, "clause": "Para 64"},
        {"number": "12.2", "text": "Do new employees receive cyber security awareness training as part of their induction programme?", "points": 8, "clause": "Para 65"},
        {"number": "12.3", "text": "Is ongoing cyber security education provided to all staff at least annually?", "points": 8, "clause": "Para 67"},
        {"number": "12.4", "text": "Are cyber security exercises conducted to test staff awareness and response capabilities?", "points": 8, "clause": "Para 68"},
        {"number": "12.5", "text": "Is training provided to staff when they move into new roles with different security responsibilities?", "points": 6, "clause": "Para 66"},
        {"number": "12.6", "text": "Are training completion records maintained and reported to Senior Management?", "points": 6, "clause": "Para 67"},
        {"number": "12.7", "text": "Does the institution track and demonstrate competence levels for staff in key cyber security roles?", "points": 8, "clause": "Para 64"},
    ],
    "13": [
        {"number": "13.1", "text": "Is there a formal process for assessing and approving direct connectivity to external parties including fintechs and business partners?", "points": 10, "clause": "Para 69"},
        {"number": "13.2", "text": "Are connections to other financial institutions and non-regulated entities subject to security controls and monitoring?", "points": 8, "clause": "Para 70"},
        {"number": "13.3", "text": "Do contracts with business partners include cyber security requirements and the right to audit?", "points": 10, "clause": "Para 71"},
        {"number": "13.4", "text": "Is remote access by external parties strictly controlled, monitored and time-limited?", "points": 10, "clause": "Para 72"},
        {"number": "13.5", "text": "Are all external parties subject to security assessment before being granted access to institutional systems?", "points": 8, "clause": "Para 73"},
        {"number": "13.6", "text": "Is data in motion between the institution and external parties protected through encryption and integrity controls?", "points": 8, "clause": "Para 74"},
    ],
    "14": [
        {"number": "14.1", "text": "Is there a formal cloud governance policy covering risk assessment, approval and ongoing oversight of cloud services?", "points": 10, "clause": "Para 75"},
        {"number": "14.2", "text": "Are cloud services subject to formal risk assessment before adoption covering data sovereignty, availability and exit risks?", "points": 10, "clause": "Para 76"},
        {"number": "14.3", "text": "Do cloud service contracts include security requirements, data ownership clauses, audit rights and incident notification obligations?", "points": 10, "clause": "Para 77"},
        {"number": "14.4", "text": "Is sensitive financial data stored only within Ghana's borders in compliance with the data sovereignty requirement?", "points": 10, "clause": "Para 75"},
        {"number": "14.5", "text": "Are only non-sensitive front-end services hosted in the cloud under a risk-based approved framework?", "points": 8, "clause": "Para 75"},
        {"number": "14.6", "text": "Is there an exit strategy documented for each cloud service in case the provider relationship ends?", "points": 6, "clause": "Para 77"},
    ],
    "15": [
        {"number": "15.1", "text": "For foreign banks operating in Ghana — do they comply with all BoG CISD requirements in addition to their home country regulations?", "points": 10, "clause": "Para 80"},
        {"number": "15.2", "text": "For Ghanaian banks abroad — do overseas operations maintain security standards consistent with the CISD?", "points": 10, "clause": "Para 81"},
        {"number": "15.3", "text": "Are cross-border data transfers subject to controls ensuring compliance with Ghanaian data protection requirements?", "points": 10, "clause": "Para 80"},
        {"number": "15.4", "text": "Is there clear escalation and reporting to BoG for significant cyber incidents affecting international operations?", "points": 8, "clause": "Para 80"},
    ],
    "16": [
        {"number": "16.1", "text": "Is there a formal physical security policy covering all locations where ICT assets and sensitive data are held?", "points": 8, "clause": "Para 82"},
        {"number": "16.2", "text": "Are secured zones established with physical access controls restricting entry to authorised personnel only?", "points": 10, "clause": "Para 83"},
        {"number": "16.3", "text": "Is physical segmentation implemented to separate critical ICT infrastructure from general office areas?", "points": 8, "clause": "Para 84"},
        {"number": "16.4", "text": "Are all hardware assets physically secured against theft, tampering and unauthorised access?", "points": 8, "clause": "Para 85"},
        {"number": "16.5", "text": "Are physical access logs maintained and reviewed regularly for all secured zones?", "points": 6, "clause": "Para 83"},
    ],
    "17": [
        {"number": "17.1", "text": "Are pre-employment background checks conducted for all staff, especially those in sensitive or privileged roles?", "points": 10, "clause": "Para 86"},
        {"number": "17.2", "text": "Is there a formal process for revoking all system access promptly upon employee termination?", "points": 10, "clause": "Para 87"},
        {"number": "17.3", "text": "Are employees in sensitive positions subject to periodic re-vetting and enhanced monitoring?", "points": 8, "clause": "Para 88"},
        {"number": "17.4", "text": "Is there a documented employee lifecycle process covering onboarding, role changes and offboarding from a security perspective?", "points": 8, "clause": "Para 89"},
        {"number": "17.5", "text": "Are employees required to acknowledge and sign the institution's cyber security policies as part of their employment conditions?", "points": 6, "clause": "Para 86"},
    ],
    "18": [
        {"number": "18.1", "text": "Do all contracts with ICT vendors and service providers include formal cyber security requirements?", "points": 10, "clause": "Para 90"},
        {"number": "18.2", "text": "Do vendor contracts include the right to audit security controls and request evidence of compliance?", "points": 10, "clause": "Para 90"},
        {"number": "18.3", "text": "Are vendor security obligations reviewed and updated when contracts are renewed or services change?", "points": 8, "clause": "Para 90"},
        {"number": "18.4", "text": "Is there a vendor risk register tracking all third-party relationships and their associated security risks?", "points": 8, "clause": "Para 90"},
        {"number": "18.5", "text": "Are critical vendors subject to periodic security assessments to verify compliance with contractual security requirements?", "points": 8, "clause": "Para 90"},
    ],
    "19": [
        {"number": "19.1", "text": "Is the institution ISO 27001 certified or is there a documented plan with timeline to achieve certification?", "points": 10, "clause": "Para 4(9)"},
        {"number": "19.2", "text": "Has the institution adopted ISO 27032 guidelines for cybersecurity as recommended by the CISD?", "points": 8, "clause": "Para 4(9)"},
        {"number": "19.3", "text": "Is there a functioning Information Security Management System (ISMS) covering all key security domains?", "points": 10, "clause": "Para 4(9)"},
        {"number": "19.4", "text": "Is the ISMS subject to regular internal and external audits with findings tracked to resolution?", "points": 8, "clause": "Para 4(9)"},
        {"number": "19.5", "text": "Are ISMS policies and procedures reviewed at least annually and updated to reflect changes in the threat landscape?", "points": 8, "clause": "Para 4(9)"},
        {"number": "19.6", "text": "Is senior management commitment to the ISMS demonstrated through resource allocation and active participation in reviews?", "points": 6, "clause": "Para 4(9)"},
    ],
    "20": [
        {"number": "20.1", "text": "Is there a documented Business Continuity Plan (BCP) covering cyber incident scenarios?", "points": 10, "clause": "Para 5(2)"},
        {"number": "20.2", "text": "Is there a Disaster Recovery Plan (DRP) with defined Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)?", "points": 10, "clause": "Para 5(2)"},
        {"number": "20.3", "text": "Are BCP and DRP tests conducted at least annually with results documented and lessons learned acted upon?", "points": 10, "clause": "Para 7(4)"},
        {"number": "20.4", "text": "Are backup systems in place for all critical data and systems with backups tested regularly for recoverability?", "points": 10, "clause": "Para 5(2)"},
        {"number": "20.5", "text": "Are backup copies stored securely offsite or in a separate location from primary systems?", "points": 8, "clause": "Para 5(2)"},
        {"number": "20.6", "text": "Is there a crisis communication plan covering internal and external communications during a cyber incident?", "points": 6, "clause": "Para 5(2)"},
        {"number": "20.7", "text": "Are all critical third-party dependencies identified in the BCP with contingency plans if they become unavailable?", "points": 8, "clause": "Para 5(2)"},
    ],
    "21": [
        {"number": "21.1", "text": "Has the institution developed a formal policy for the governance and risk management of AI systems used in operations or customer services?", "points": 10, "clause": "Para 91"},
        {"number": "21.2", "text": "Are AI systems subject to security testing, bias assessment and explainability reviews before deployment?", "points": 10, "clause": "Para 91"},
        {"number": "21.3", "text": "Where blockchain technology is used, has the institution conducted a formal risk assessment covering smart contract vulnerabilities and key management risks?", "points": 10, "clause": "Para 91"},
        {"number": "21.4", "text": "If the institution handles virtual assets, has it implemented controls aligned with AML/CFT requirements and BoG guidance?", "points": 10, "clause": "Para 91"},
        {"number": "21.5", "text": "Is there a designated owner responsible for overseeing the institution's digital innovation risk framework?", "points": 8, "clause": "Para 91"},
        {"number": "21.6", "text": "Are third-party AI tools and blockchain platforms subject to the same vendor due diligence requirements as other outsourced ICT services?", "points": 8, "clause": "Para 91"},
        {"number": "21.7", "text": "Does the institution have an incident response procedure specifically covering AI model failure, blockchain disruption or virtual asset compromise?", "points": 8, "clause": "Para 91"},
    ],
    "22": [
        {"number": "22.1",  "text": "Is there a formal governance framework for data centre operations including defined roles, responsibilities and escalation procedures?", "points": 10, "clause": "Para 92"},
        {"number": "22.2",  "text": "Does the data centre have a tested Business Continuity and Disaster Recovery Plan with documented RTO and RPO targets?", "points": 10, "clause": "Para 93"},
        {"number": "22.3",  "text": "Has a site risk assessment been conducted covering external threats such as flooding, power grid instability and proximity to hazardous facilities?", "points": 8, "clause": "Para 94"},
        {"number": "22.4",  "text": "Are redundant power systems including UPS and generators in place with regular load testing to ensure continuity during outages?", "points": 10, "clause": "Para 95"},
        {"number": "22.5",  "text": "Are cooling and environmental control systems monitored in real time with automated alerts for temperature and humidity thresholds?", "points": 8, "clause": "Para 96"},
        {"number": "22.6",  "text": "Is there a fire suppression system appropriate for ICT equipment with regular testing and maintenance records?", "points": 8, "clause": "Para 97"},
        {"number": "22.7",  "text": "Is structured cabling documented, labelled and physically protected against tampering or accidental disconnection?", "points": 6, "clause": "Para 98"},
        {"number": "22.8",  "text": "Is physical access to the data centre restricted to authorised personnel with multi-factor authentication and logged entry/exit records?", "points": 10, "clause": "Para 99"},
        {"number": "22.9",  "text": "Where multiple tenants share a data centre facility, is adequate segregation of systems, networks and physical spaces maintained?", "points": 8, "clause": "Para 100"},
        {"number": "22.10", "text": "Is there 24/7 monitoring of data centre infrastructure with documented incident response procedures for physical and technical events?", "points": 10, "clause": "Para 101"},
        {"number": "22.11", "text": "Do colocation or hosting contracts include explicit security requirements, audit rights and SLA provisions aligned with this directive?", "points": 8, "clause": "Para 102"},
        {"number": "22.12", "text": "Is there a regular vulnerability assessment and maintenance schedule for all data centre facility systems?", "points": 8, "clause": "Para 103"},
        {"number": "22.13", "text": "Does all sensitive customer and financial data remain physically stored within Ghana's territorial boundaries as required by the Cybersecurity Act 2020?", "points": 10, "clause": "Para 104"},
    ],
    "23": [
        {"number": "23.1", "text": "Has the institution developed a formal API security policy covering authentication, authorisation, rate limiting and data exposure controls?", "points": 10, "clause": "Para 38"},
        {"number": "23.2", "text": "Are all external-facing APIs protected by strong authentication mechanisms such as OAuth 2.0, API keys or mutual TLS?", "points": 10, "clause": "Para 38"},
        {"number": "23.3", "text": "Is an API gateway in place to centralise access control, logging and threat detection for all API traffic?", "points": 10, "clause": "Para 38"},
        {"number": "23.4", "text": "Are APIs regularly tested for OWASP API Security Top 10 vulnerabilities including broken object level authorisation and excessive data exposure?", "points": 10, "clause": "Para 38"},
        {"number": "23.5", "text": "Is there a formal API inventory documenting all internal and external APIs, their owners, consumers and data sensitivity levels?", "points": 8, "clause": "Para 38"},
        {"number": "23.6", "text": "Are third-party APIs integrated into the institution's systems subject to the same security assessment as other vendor services?", "points": 8, "clause": "Para 38"},
    ],
}

# ── SEED THE DATABASE ─────────────────────────────────────────────────────────
total_sections = 0
total_questions = 0

for section_data in SECTIONS:
    section = DirectiveSection.objects.create(
        number=section_data["number"],
        title=section_data["title"],
        weight=section_data["weight"],
        risk_level=section_data["risk_level"],
        directive_reference=section_data["directive_reference"],
        order=section_data["order"],
    )
    total_sections += 1

    questions = QUESTIONS.get(section_data["number"], [])
    for i, q in enumerate(questions):
        Question.objects.create(
            section=section,
            question_number=q["number"],
            text=q["text"],
            max_points=q["points"],
            directive_clause=q["clause"],
            order=i + 1,
        )
        total_questions += 1

    print(f"  ✓ Section {section_data['number']} — {section_data['title']} ({len(questions)} questions)")

print(f"\n✅ Seeding complete!")
print(f"   Sections: {total_sections}")
print(f"   Questions: {total_questions}")
print(f"\nAxiomGH is ready. Start your first assessment at http://localhost:3000")
