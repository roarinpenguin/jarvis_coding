[
  {
    "timestamp": "2025-08-04T21:48:50.655945Z",
    "scenario": "malware_outbreak",
    "platform": "email",
    "event_index": 0,
    "malicious": true,
    "raw_event": "{\"GUID\":\"71671e7d-91c8-432b-a858-977e99c355a9\",\"QID\":\"Q886237\",\"id\":\"1d8f3157-0c69-4c1a-b2b2-c2d39b86c6b0\",\"messageID\":\"<ee0ca2ec-c23c-444a-bfbd-635073bbc1c8@suspicious-domain-89.org>\",\"messageTime\":\"2025-08-04T23:45:46.657Z\",\"messageSize\":428005,\"subject\":\"Urgent: Account verification required\",\"sender\":\"security@phishing-site.com\",\"fromAddress\":[\"help615@suspicious-domain-89.org\"],\"headerFrom\":\"\\\"Grace Miller\\\" <help615@suspicious-domain-89.org>\",\"senderIP\":\"10.201.243.241\",\"recipient\":[\"noreply@corporate.com\"],\"toAddresses\":[\"noreply@corporate.com\"],\"ccAddresses\":[],\"replyToAddress\":[\"help615@suspicious-domain-89.org\"],\"headerReplyTo\":\"help615@suspicious-domain-89.org\",\"completelyRewritten\":\"true\",\"cluster\":\"proofpoint-cluster-1\",\"policyRoutes\":[\"block\"],\"modulesRun\":[\"spf\",\"dkimv\",\"impostor\"],\"spamScore\":0,\"phishScore\":55,\"malwareScore\":0,\"impostorScore\":87,\"threatsInfo\":[{\"threat\":\"Brand Impersonation\",\"threatType\":\"impostor\",\"threatID\":\"92cf4ad2-16e7-47c9-b36b-9e367a88993d\",\"threatStatus\":\"active\",\"classification\":\"impostor\",\"threatTime\":\"2025-08-04T23:45:46.657Z\"}],\"messageParts\":[{\"disposition\":\"inline\",\"contentType\":\"text/plain\",\"oContentType\":\"text/plain\",\"isUnsupported\":false}],\"spf\":\"pass\",\"dkimv\":\"fail\",\"dmarc\":\"pass\",\"xmailer\":\"Thunderbird\",\"campaignId\":\"campaign_a6bf1f7a\",\"threatType\":\"phish\"}",
    "attr_fields": {
      "dataSource.vendor": "Proofpoint",
      "dataSource.name": "Proofpoint",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "Proofpoint",
      "metadata.product.name": "Proofpoint Email Protection",
      "metadata.version": "1.0.0"
    }
  },
  {
    "timestamp": "2025-08-04T21:53:20.655945Z",
    "scenario": "malware_outbreak",
    "platform": "email",
    "event_index": 1,
    "malicious": true,
    "raw_event": "{\"GUID\":\"55136e12-521a-4a83-9724-1b16d7945ef6\",\"QID\":\"Q505401\",\"id\":\"9e1ab11f-64f3-44c4-86f8-29d4b7e0f6f4\",\"messageID\":\"<7948ad41-6717-4a04-a52a-8894161fa485@corporate.com>\",\"messageTime\":\"2025-08-04T23:44:12.658Z\",\"messageSize\":157695,\"subject\":\"Urgent: Account verification required\",\"sender\":\"security@phishing-site.com\",\"fromAddress\":[\"diana.davis@corporate.com\"],\"headerFrom\":\"\\\"Grace Miller\\\" <diana.davis@corporate.com>\",\"senderIP\":\"221.49.160.44\",\"recipient\":[\"noreply@corporate.com\"],\"toAddresses\":[\"noreply@corporate.com\"],\"ccAddresses\":[],\"replyToAddress\":[\"diana.davis@corporate.com\"],\"headerReplyTo\":\"diana.davis@corporate.com\",\"completelyRewritten\":\"false\",\"cluster\":\"proofpoint-cluster-9\",\"policyRoutes\":[\"deliver\"],\"modulesRun\":[\"urldefense\",\"spf\",\"spam\",\"av\",\"attachment_defense\",\"dmarc\"],\"spamScore\":22,\"phishScore\":9,\"malwareScore\":0,\"impostorScore\":8,\"messageParts\":[{\"disposition\":\"inline\",\"contentType\":\"text/plain\",\"oContentType\":\"text/plain\",\"isUnsupported\":false}],\"spf\":\"neutral\",\"dkimv\":\"none\",\"dmarc\":\"none\",\"xmailer\":\"Microsoft Outlook 16.0\",\"threatType\":\"phish\"}",
    "attr_fields": {
      "dataSource.vendor": "Proofpoint",
      "dataSource.name": "Proofpoint",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "Proofpoint",
      "metadata.product.name": "Proofpoint Email Protection",
      "metadata.version": "1.0.0"
    }
  },
  {
    "timestamp": "2025-08-04T21:57:50.655945Z",
    "scenario": "malware_outbreak",
    "platform": "endpoint",
    "event_index": 2,
    "malicious": true,
    "raw_event": "CEF:0|CrowdStrike|Falcon|6.35.15406.0|6987|Credential Theft Attempt|10|rt=1754351330658 start=1754348127232 end=0 dvchost=DEV-MACHINE-02 duser=Administrator suid=S-1-5-21-973887106-624254402-7574-5610 externalId=ldt:264e7954de32039a:693774801146 msg=Suspicious activity detected: Credential Theft Attempt fname=powershell.exe filePath=C:\\\\Users\\\\admin\\\\Downloads\\\\ cs1=rundll32.exe -enc 9f6a3e6f cs1Label=CommandLine fileHash=4f42ba310bad9a3a6834f5b98ac60de2e0b5e354f9389dd900bf63e49e04ef3d oldFileHash=02ba9b23689570c2eac1cd02ac993a5c9e9c5c58 fileHashMd5=ae5dd8cd63f90f6aac6b79ca9dc1940a dntdom=CORP src=10.109.129.148 dst=10.213.67.197 dpt=8443 proto=UDP spt=60745 deviceDirection=1 cs2=CredentialDumpTool cs2Label=EventSimpleName deviceProcessId=9539 deviceProcessName=cscript.exe act=detected cat=Credential Dumping cs3=T1003 cs3Label=TechniqueId cs4=Emotet cs4Label=ThreatFamily event_simpleName=ProcessRollup2 name=Malware Detected",
    "attr_fields": {
      "dataSource.vendor": "CrowdStrike",
      "dataSource.name": "CrowdStrike Endpoint",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "CrowdStrike",
      "metadata.product.name": "CrowdStrike Falcon",
      "metadata.version": "1.0.0"
    }
  },
  {
    "timestamp": "2025-08-04T22:02:20.655945Z",
    "scenario": "malware_outbreak",
    "platform": "endpoint",
    "event_index": 3,
    "malicious": true,
    "raw_event": "CEF:0|CrowdStrike|Falcon|6.35.15406.0|3334|File System Activity|3|rt=1754351330658 start=1754348347025 end=0 dvchost=SERVER-DC01 duser=asmith suid=S-1-5-21-959945806-706572745-1908-3105 externalId=ldt:f5c085d9e3b3163d:546702187479 msg=Suspicious activity detected: File System Activity fname=wmic.exe filePath=C:\\\\ProgramData\\\\ cs1=mshta.exe /c 4b4acecf cs1Label=CommandLine fileHash=95d5f90e9d9e2226fcfc4767c44fce1823141c53e83b039d25336c713af3641a oldFileHash=3997c6f9354a2e4afe7360925d05b273659f6d4c fileHashMd5=ae56401b3783a193defe342dae64f428 dntdom=CORP src=10.57.99.66 dst=10.99.231.83 dpt=445 proto=UDP spt=52975 deviceDirection=0 cs2=FileWritten cs2Label=EventSimpleName deviceProcessId=8700 deviceProcessName=regsvr32.exe act=detected event_simpleName=ProcessRollup2 name=Malware Detected cs4=Emotet cs4Label=ThreatFamily",
    "attr_fields": {
      "dataSource.vendor": "CrowdStrike",
      "dataSource.name": "CrowdStrike Endpoint",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "CrowdStrike",
      "metadata.product.name": "CrowdStrike Falcon",
      "metadata.version": "1.0.0"
    }
  },
  {
    "timestamp": "2025-08-04T22:06:50.655945Z",
    "scenario": "malware_outbreak",
    "platform": "endpoint",
    "event_index": 4,
    "malicious": true,
    "raw_event": "CEF:0|CrowdStrike|Falcon|6.35.15406.0|6270|Lateral Movement Detected|8|rt=1754351330658 start=1754351170299 end=0 dvchost=WORKSTATION-005 duser=jdoe suid=S-1-5-21-796925352-860299136-9076-1106 externalId=ldt:2b081e2f646b0294:207486666766 msg=Suspicious activity detected: Lateral Movement Detected fname=regsvr32.exe filePath=C:\\\\Users\\\\jdoe\\\\AppData\\\\Local\\\\Temp\\\\ cs1=regsvr32.exe -enc 1efd0be2 cs1Label=CommandLine fileHash=47d7105586809abffb6646dc2c6fc4d99a9790bffdc1e42a342609fa69be3f8e oldFileHash=74d2024020c6d2a21f3e0fba17157b68e5a5a3a8 fileHashMd5=3cc12b6b1e250039f64ca6f60580b886 dntdom=INTERNAL src=10.61.113.90 dst=10.80.189.234 dpt=3389 proto=TCP spt=50758 deviceDirection=1 cs2=LateralMovement cs2Label=EventSimpleName deviceProcessId=3909 deviceProcessName=cscript.exe act=detected shost=WORKSTATION-005 dhost=SERVER-38 cs3=PSExec cs3Label=LateralMovementTechnique cs4=Emotet cs4Label=ThreatFamily cs5=ADMIN$ cs5Label=ShareName cat=Remote Services cs6=T1021 cs6Label=TechniqueId event_simpleName=ProcessRollup2 name=Malware Detected",
    "attr_fields": {
      "dataSource.vendor": "CrowdStrike",
      "dataSource.name": "CrowdStrike Endpoint",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "CrowdStrike",
      "metadata.product.name": "CrowdStrike Falcon",
      "metadata.version": "1.0.0"
    }
  },
  {
    "timestamp": "2025-08-04T22:11:20.655945Z",
    "scenario": "malware_outbreak",
    "platform": "endpoint",
    "event_index": 5,
    "malicious": true,
    "raw_event": "CEF:0|CrowdStrike|Falcon|6.35.15406.0|9716|Registry Modification|5|rt=1754351330659 start=1754348786395 end=0 dvchost=SERVER-DC01 duser=admin suid=S-1-5-21-174476654-673512506-6673-1729 externalId=ldt:a787253838eb0c2a:145850029849 msg=Suspicious activity detected: Registry Modification fname=wscript.exe filePath=C:\\\\Program Files\\\\ cs1=mshta.exe -Command 5221aa82 cs1Label=CommandLine fileHash=87b48fa4c63a21a38812b1514e9637681bb282380b06df78c89c8b28ccd3249c oldFileHash=54844844ff972b2aa2a230abe4aad3e11b280749 fileHashMd5=1fb7a8bccc1ec391bb2431afca062e0e dntdom=CORP src=10.156.242.173 dst=10.119.192.165 dpt=443 proto=TCP spt=51092 deviceDirection=1 cs2=RegistryOperationDetectInfo cs2Label=EventSimpleName deviceProcessId=2032 deviceProcessName=wscript.exe act=detected event_simpleName=ProcessRollup2 name=Malware Detected cs4=Emotet cs4Label=ThreatFamily",
    "attr_fields": {
      "dataSource.vendor": "CrowdStrike",
      "dataSource.name": "CrowdStrike Endpoint",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "CrowdStrike",
      "metadata.product.name": "CrowdStrike Falcon",
      "metadata.version": "1.0.0"
    }
  },
  {
    "timestamp": "2025-08-04T22:15:50.655945Z",
    "scenario": "malware_outbreak",
    "platform": "endpoint",
    "event_index": 6,
    "malicious": true,
    "raw_event": "CEF:0|CrowdStrike|Falcon|6.35.15406.0|3174|Network Connection Blocked|5|rt=1754351330659 start=1754351157312 end=0 dvchost=DEV-MACHINE-02 duser=jdoe suid=S-1-5-21-383198423-511616786-7733-6233 externalId=ldt:c9a2b21ce0e20258:729659702688 msg=Suspicious activity detected: Network Connection Blocked fname=regsvr32.exe filePath=C:\\\\Windows\\\\Temp\\\\ cs1=cscript.exe -enc 1b4bbd39 cs1Label=CommandLine fileHash=7a1f0a10fe83508d398636665c2e059c605f452f9e39a00c66abe66cd6307713 oldFileHash=c58cd593e85048f5054a5a9813b474c43be71007 fileHashMd5=e4abc9950198e1d9230b16c52f3d293b dntdom=INTERNAL src=10.173.150.2 dst=10.220.12.207 dpt=443 proto=UDP spt=64738 deviceDirection=0 cs2=NetworkConnectIP4 cs2Label=EventSimpleName deviceProcessId=7354 deviceProcessName=wscript.exe act=detected cs3=Outgoing cs3Label=ConnectionDirection cs4=Emotet cs4Label=ThreatFamily request=suspicious-174.net app=DNS event_simpleName=ProcessRollup2 name=Malware Detected",
    "attr_fields": {
      "dataSource.vendor": "CrowdStrike",
      "dataSource.name": "CrowdStrike Endpoint",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "CrowdStrike",
      "metadata.product.name": "CrowdStrike Falcon",
      "metadata.version": "1.0.0"
    }
  },
  {
    "timestamp": "2025-08-04T22:20:20.655945Z",
    "scenario": "malware_outbreak",
    "platform": "network",
    "event_index": 7,
    "malicious": true,
    "raw_event": "{\"time\":1754351330659,\"creationTime\":1754351228659,\"model\":{\"name\":\"Anomalous Connection / Data Sent to Rare Domain\",\"description\":\"Device sending data to suspicious domain\"},\"breachUrl\":\"https://darktrace-291bf425-0001-01/#modelbreach/85260\",\"pbid\":8447597,\"score\":0.85,\"device\":{\"hostname\":\"IOT-318\",\"ip\":\"10.25.255.28\",\"mac\":\"f9:32:9a:16:54:37\",\"type\":\"iot\",\"os\":\"Unknown\"},\"triggeredComponents\":[{\"time\":1754351330659,\"uid\":\"4d649f4f-4555-4ae1-a456-734803dd9942\",\"pid\":2293,\"detail\":{\"fileName\":\"chrome_update.exe\",\"fileHash\":\"e7714fa462444d4b96a834b3c417c32f\",\"fileSize\":776197,\"downloadSource\":\"http://crypto-miner-31.io/download\"}}],\"commentCount\":0,\"acknowledged\":false,\"category\":\"malware\",\"mitreTactics\":[\"Execution\",\"Defense Evasion\"],\"tags\":[\"darktrace\",\"anomaly\",\"security\",\"malware\",\"trojan\",\"virus\"],\"externalDomain\":\"malicious-c2.com\"}",
    "attr_fields": {
      "dataSource.vendor": "Darktrace",
      "dataSource.name": "Darktrace",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "Darktrace",
      "metadata.product.name": "Darktrace Enterprise Immune System",
      "metadata.version": "1.0.0"
    }
  },
  {
    "timestamp": "2025-08-04T22:24:50.655945Z",
    "scenario": "malware_outbreak",
    "platform": "network",
    "event_index": 8,
    "malicious": true,
    "raw_event": "{\"time\":1754351330659,\"incidentId\":\"2d1b1346-26f1-48bb-bf99-a5b92273e68a\",\"title\":\"Potential Data Exfiltration\",\"summary\":\"Large data transfer to unusual external destination\",\"category\":\"exfiltration\",\"groupSeverity\":85,\"incidentUrl\":\"https://darktrace-bd97cb72-0001-01/saas#aiincident/60493\",\"startTime\":1754349000659,\"endTime\":1754350621659,\"devices\":[{\"hostname\":\"DESKTOP-845\",\"ip\":\"10.239.23.232\",\"mac\":\"40:6a:7a:80:75:dd\",\"type\":\"desktop\",\"os\":\"macOS 12.0\"},{\"hostname\":\"DESKTOP-950\",\"ip\":\"10.230.136.126\",\"mac\":\"2f:08:7a:eb:51:9b\",\"type\":\"iot\",\"os\":\"Unknown\"},{\"hostname\":\"ROUTER-998\",\"ip\":\"10.65.43.254\",\"mac\":\"67:3c:3d:ee:e1:09\",\"type\":\"server\",\"os\":\"Unknown\"}],\"relatedBreaches\":[{\"modelName\":\"Device / New User Agent\",\"pbid\":1548107,\"time\":1754349000659,\"score\":0.554,\"device\":{\"hostname\":\"DESKTOP-950\",\"ip\":\"10.230.136.126\",\"mac\":\"2f:08:7a:eb:51:9b\",\"type\":\"iot\",\"os\":\"Unknown\"}},{\"modelName\":\"Anomalous File / Internet Facing System File Download\",\"pbid\":8609622,\"time\":1754350591659,\"score\":0.655,\"device\":{\"hostname\":\"DESKTOP-950\",\"ip\":\"10.230.136.126\",\"mac\":\"2f:08:7a:eb:51:9b\",\"type\":\"iot\",\"os\":\"Unknown\"}},{\"modelName\":\"Device / Suspicious Domain\",\"pbid\":1373931,\"time\":1754350621659,\"score\":0.792,\"device\":{\"hostname\":\"DESKTOP-845\",\"ip\":\"10.239.23.232\",\"mac\":\"40:6a:7a:80:75:dd\",\"type\":\"desktop\",\"os\":\"macOS 12.0\"}}],\"mitreTactics\":[\"Unknown\"],\"mitreAttacks\":[\"T1041\",\"T1048\",\"T1567\"],\"status\":\"investigating\",\"assignee\":\"incident_response\",\"comments\":[],\"exfiltrationDetails\":{\"totalBytesTransferred\":242980372,\"destinations\":[\"malware-c2-0.net\",\"suspicious-domain-1.com\",\"suspicious-domain-2.com\"],\"protocols\":[\"HTTPS\",\"SSH\",\"FTP\"],\"duration\":1621000},\"investigationNotes\":\"User confirmed unusual but authorized activity\",\"model\":{\"name\":\"Anomalous Connection / Data Sent to Rare Domain\",\"description\":\"Device sending data to suspicious domain\"},\"score\":0.85,\"externalDomain\":\"malicious-c2.com\"}",
    "attr_fields": {
      "dataSource.vendor": "Darktrace",
      "dataSource.name": "Darktrace",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "Darktrace",
      "metadata.product.name": "Darktrace Enterprise Immune System",
      "metadata.version": "1.0.0"
    }
  },
  {
    "timestamp": "2025-08-04T22:29:20.655945Z",
    "scenario": "malware_outbreak",
    "platform": "network",
    "event_index": 9,
    "malicious": true,
    "raw_event": "{\"time\":1754351330659,\"incidentId\":\"ee4777ca-3f55-4635-9701-d1c57163f805\",\"title\":\"Suspicious Remote Access Pattern\",\"summary\":\"Unusual remote access activity detected from external source\",\"category\":\"remote_access\",\"groupSeverity\":75,\"incidentUrl\":\"https://darktrace-ca41d723-0001-01/saas#aiincident/21476\",\"startTime\":1754348303659,\"endTime\":1754350159659,\"devices\":[{\"hostname\":\"ROUTER-226\",\"ip\":\"10.1.18.199\",\"mac\":\"cf:7e:b9:29:1c:72\",\"type\":\"desktop\",\"os\":\"Ubuntu 20.04\"},{\"hostname\":\"SERVER-606\",\"ip\":\"10.143.163.157\",\"mac\":\"8f:2e:a3:e4:1e:da\",\"type\":\"router\",\"os\":\"Windows 11\"}],\"relatedBreaches\":[{\"modelName\":\"Device / Large Number of Model Breaches\",\"pbid\":2160219,\"time\":1754348303659,\"score\":0.782,\"device\":{\"hostname\":\"ROUTER-226\",\"ip\":\"10.1.18.199\",\"mac\":\"cf:7e:b9:29:1c:72\",\"type\":\"desktop\",\"os\":\"Ubuntu 20.04\"}},{\"modelName\":\"Device / New User Agent\",\"pbid\":3057360,\"time\":1754349508659,\"score\":0.798,\"device\":{\"hostname\":\"SERVER-606\",\"ip\":\"10.143.163.157\",\"mac\":\"8f:2e:a3:e4:1e:da\",\"type\":\"router\",\"os\":\"Windows 11\"}},{\"modelName\":\"Device / New User Agent\",\"pbid\":2454654,\"time\":1754350159659,\"score\":0.594,\"device\":{\"hostname\":\"ROUTER-226\",\"ip\":\"10.1.18.199\",\"mac\":\"cf:7e:b9:29:1c:72\",\"type\":\"desktop\",\"os\":\"Ubuntu 20.04\"}}],\"mitreTactics\":[\"Initial Access\",\"Persistence\"],\"mitreAttacks\":[\"T1133\",\"T1078\",\"T1021\"],\"status\":\"false_positive\",\"assignee\":\"soc_analyst_1\",\"comments\":[],\"investigationNotes\":\"Confirmed malicious activity, containment in progress\",\"model\":{\"name\":\"Anomalous Connection / Data Sent to Rare Domain\",\"description\":\"Device sending data to suspicious domain\"},\"score\":0.85,\"externalDomain\":\"malicious-c2.com\"}",
    "attr_fields": {
      "dataSource.vendor": "Darktrace",
      "dataSource.name": "Darktrace",
      "dataSource.category": "security",
      "metadata.product.vendor_name": "Darktrace",
      "metadata.product.name": "Darktrace Enterprise Immune System",
      "metadata.version": "1.0.0"
    }
  }
]