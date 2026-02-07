import pandas as pd

def get_found_vulnearbilities(scan_report_filepath: str):
    scan_report = pd.read_csv(scan_report_filepath)

    oids = scan_report['NVT OID'].to_dict()

    return oids

def extract_vulnerability_details(report_filepath: str, oid: str):
    headers = ['CVEs','NVT Name','Port','Port Protocol','Summary', 'Specific Result', 'Vulnerability Detection Method','Affected Software/OS']

    report = pd.read_csv(report_filepath)
    line = report[report['NVT OID'].astype(str) == oid]
    
    if line.empty:
        print(f"ERRO: OID '{oid}' não foi encontrado no CSV. Nenhum OID corresponde exatamente.")
        raise ValueError(f"OID '{oid}' não encontrado no relatório.") 

    line = line.index[0]

    vuln_details = {}
    for header in headers:
        content = report.loc[line, header]
        vuln_details[header] = content
    
    return vuln_details
