import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from datetime import date
import pandas as pd
import streamlit as st
from streamlit.components.v1 import iframe

import snowflake.connector

st.set_page_config(layout="centered", page_title="Inspection Report PDF Generator")
st.title("Inspection Report PDF Generator")

st.write(
    "This app lets you get data from snowflake, generate & download a report in PDF format."
)

# Initialize connection.
# Uses st.experimental_singleton to only run once.
# @st.experimental_singleton
def init_connection():
    return snowflake.connector.connect(**st.secrets["snowflake"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def get_snowflake_data(property):
    sql = """
            SELECT UNIQUEID,
            OPERATINGGROUP,
            BUSINESSGROUP,
            COMPANY,
            FRANCHISE,
            PROPERTY,
            REGION,
            COUNTRY,
            SUBBUSINESS,
            INSPECTIONSITETYPE,
            SEGMENT,
            CLIENT_FIRST_APPROVAL,
            OTHER_INSPECTING_ORG,
            INSPECTING_ORG_OR_ISSUEAGENCY,
            CREATEDBY,
            CREATEDDATE,
            ONSITEVISIT,
            INSPECTIONDAYS,
            FDA_REPORT_RECEIVED,
            OTHER_TYPEOF_REPORTISSUED,
            WHY_WAS_THEINSPECTIONCLASSIFIED_ASSIGNIFICANT,
            NOTIFICATIONDATE,
            TYPEOF_REPORTISSUED,
            DATE_REPORT_ISSUED_OR_EXP,
            SIGNIFICANT_INSPECTION_STATUS_FOLLOWUP,
            UNANNOUNCED,
            ENDDATE,
            INSPECTION_REPORTISSUED,
            INSPECTION_ORIGINALLY_SCHEDULED,
            SIGNIFICANT_INSPECTIONSTATUS,
            DATEREVIEWED,
            REVIEWEDBY,
            ISSIGNIFICANT_INSPECTION,
            TYPEOFACTION,
            INSPECTION_SITEVISIT_STATUS,
            STARTDATE,
            TYPEOF_REGULATORY_ACTION,
            CRITICALEM,
            SEVERITY,
            CATEGORIES1,
            CATEGORIES2,
            CATEGORIES3,
            REPEAT,
            COMMENTS,
            BRIEF_SUMMARYOF_INSPECTION,
            CRITICALOBSERVATIONS,
            MAJOROBSERVATIONS,
            MINOROBSERVATIONS,
            OTHEROBSERVATIONS
            FROM
            INSPECTION_REGULATORY_REPORT
            WHERE
            PROPERTY = 
    """ + "'" +property+"'"
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


options = {
    "enable-local-file-access": True
}

# Static Values
inspection_start_date = "Jan 1, 2018"
inspection_end_date = "May 24, 2018"
inspection_site_visit_status = "Closed"
criticalEM = "All"
regulatory_action = "None"
operating_group = "Medical Devices, Consumer, Non-Operating"
business_group = "Blank, Consumer MedTech, Consumer, Non-Operating, One MD"
franchise = "CHC, Consumer, Full Facility"
property = """0D9IALZ5J4 Property, 0A6TUOU1PQ Property, 0AZBJ4UNB8 Property, 0AWHQNT2S2 Property, 0BTP65JVSH Property, 
0AY4TRXIWB Property, 0C1K0KPK41 Property, 0DFOVAE2NV Property, 0CGIFDZGT1 Property, 0DZ5TL3HTW Property, 
0EELJDML4D Property, 0ESAL394PQ Property, 0EUKL2GBQL Property"""
region = "ABC"
country = """India,France,Brazil,Philippines (the),United States of America (the),Lithuania,Russian Federation (the),
Japan,China,South Africa"""

env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
template = env.get_template("template.html")


st.write("Generate Inspection Report for:")
form = st.form("template_form")
property = form.selectbox(
    "Choose property",
    ["0D9IALZ5J4 Property", "0A6TUOU1PQ Property", "0AZBJ4UNB8 Property", "0AWHQNT2S2 Property", "0BTP65JVSH Property"],
    index=0,
)
submit = form.form_submit_button("Generate PDF")

if submit:
    st.write('You selected property value:', property)
    row = get_snowflake_data(property)
    # st.write(row)

    # Dynamic Values
    operating_grp = row[0][1]
    business_grp = row[0][2]
    segment = row[0][10]
    sub_business = row[0][9]
    fran = row[0][4]
    company = row[0][3]
    prop = row[0][5]
    reg = row[0][6]
    count = row[0][7]

    # approval information
    inspect_site_type = row[0][10]
    operating_company_contact = "No Contact"
    product_name = "TEST"
    first_pass_approval = row[0][11]
    inspect_org = row[0][13]
    other_inspect_org = row[0][12]

    # inspection information
    unique_id = row[0][0]
    inspect_site_visit_status = row[0][34]
    action_type = row[0][33]
    inspect_sig = row[0][32]
    review_by = row[0][31]

    created_by = row[0][14]
    end_date = row[0][26]
    inspect_report_issued = row[0][27]
    inspect_orgi_sched = row[0][28]
    sig_inspect_stat = row[0][29]
    date_review = row[0][30]

    create_date = row[0][15]
    notifi_date = row[0][21]
    type_report_issue = row[0][32]
    date_report_issue = row[0][23]
    sig_inspect_status_follow_up = row[0][24]
    unannounced = row[0][25]

    on_site_visit = row[0][16]
    no_inspectio_day = row[0][17]
    fda_report_recieve = row[0][18]
    other_type_report_issue = row[0][19]
    why_inspect_classifi_sig = row[0][20]

    # Brief Summary & Observation Details
    obs_desc = ""
    severity = row[0][38]
    cat1 = row[0][39]
    cat2 = row[0][40]
    cat3 = row[0][41]
    repeat = row[0][42]
    comments = row[0][43]
    critical = row[0][45]
    major = row[0][46]
    minor = row[0][47]
    other = row[0][48]

    html = template.render(
        inspection_start_date=inspection_start_date,
        inspection_end_date=inspection_end_date,
        inspection_site_visit_status=inspection_site_visit_status,
        criticalEM=criticalEM,
        regulatory_action=regulatory_action,
        operating_group=operating_group,
        business_group=business_group,
        franchise=franchise,
        property=property,
        region=region,
        country=country,
        operating_grp=operating_grp,
        business_grp=business_grp,
        segment=segment,
        sub_business=sub_business,
        fran=fran,
        company=company,
        prop=prop,
        reg=reg,
        count=count,
        inspect_site_type=inspect_site_type,
        operating_company_contact=operating_company_contact,
        product_name=product_name,
        first_pass_approval=first_pass_approval,
        inspect_org=inspect_org,
        other_inspect_org=other_inspect_org,
        unique_id=unique_id,
        inspect_site_visit_status=inspect_site_visit_status,
        action_type=action_type,
        inspect_sig=inspect_sig,
        review_by=review_by,
        created_by=created_by,
        end_date=end_date,
        inspect_report_issued=inspect_report_issued,
        inspect_orgi_sched=inspect_orgi_sched,
        sig_inspect_stat=sig_inspect_stat,
        date_review=date_review,
        create_date=create_date,
        type_report_issue=type_report_issue,
        date_report_issue=date_report_issue,
        sig_inspect_status_follow_up=sig_inspect_status_follow_up,
        unannounced=unannounced,
        on_site_visit=on_site_visit,
        no_inspectio_day=no_inspectio_day,
        fda_report_recieve=fda_report_recieve,
        other_type_report_issue=other_type_report_issue,
        why_inspect_classifi_sig=why_inspect_classifi_sig,
        obs_desc="",
        severity=severity,
        cat1=cat1,
        cat2=cat2,
        cat3=cat3,
        repeat=repeat,
        comments=comments,
        critical=critical,
        major=major,
        minor=minor,
        other=other
    )

    pdf = pdfkit.from_string(html, options=options)
    # st.balloons()

    # st.success("🎉 Your pdf was generated!")
    # st.write(html, unsafe_allow_html=True)
    # st.write("")
    st.download_button(
        "⬇️ Download PDF",
        data=pdf,
        file_name="inspection_regulatory.pdf",
        mime="application/octet-stream",
    )
