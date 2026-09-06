import os
import subprocess
from pathlib import Path

def generate_html_report() -> str:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>UNIFOUND - Lost and Found Management Portal</title>
<style>
  @page {
    size: A4 portrait;
    margin: 0;
  }
  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    margin: 0;
    padding: 0;
    font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;
    color: #111;
    background: #fff;
    font-size: 10.5pt;
    line-height: 1.45;
  }
  .page {
    width: 210mm;
    height: 297mm;
    page-break-after: always;
    page-break-inside: avoid;
    padding: 12mm 14mm;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }
  .border-box {
    border: 1.5px solid #111;
    height: 100%;
    width: 100%;
    padding: 24px 28px;
    display: flex;
    flex-direction: column;
    position: relative;
  }
  h1.doc-title {
    font-size: 17pt;
    font-weight: 800;
    color: #8b0000;
    text-align: center;
    margin: 15px 0 25px;
    letter-spacing: 0.5px;
    line-height: 1.3;
  }
  h2.report-type {
    font-size: 13pt;
    font-weight: 800;
    text-align: center;
    margin: 10px 0 18px;
    text-decoration: underline;
    letter-spacing: 0.5px;
  }
  h3.degree-title {
    font-size: 11pt;
    font-weight: 700;
    text-align: center;
    margin: 6px 0;
  }
  .uni-title {
    font-size: 12pt;
    font-weight: 800;
    text-align: center;
    margin: 4px 0 20px;
    letter-spacing: 0.5px;
  }
  .session-title {
    font-size: 12pt;
    font-weight: 800;
    text-align: center;
    margin: 15px 0;
  }
  .center-text {
    text-align: center;
  }
  h1.chap-title {
    font-size: 14pt;
    font-weight: 800;
    margin: 0 0 14px 0;
    letter-spacing: 0.2px;
    text-transform: uppercase;
  }
  h2.sec-title {
    font-size: 11pt;
    font-weight: 700;
    margin: 12px 0 6px 0;
  }
  p {
    margin: 0 0 8px 0;
    text-align: justify;
    line-height: 1.42;
  }
  ul {
    margin: 4px 0 8px 0;
    padding-left: 20px;
  }
  li {
    margin-bottom: 4px;
    line-height: 1.38;
  }
  table.report-table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 9.5pt;
  }
  table.report-table th, table.report-table td {
    border: 1px solid #333;
    padding: 7px 10px;
    text-align: left;
    vertical-align: top;
  }
  table.report-table th {
    background-color: #f2f2f2;
    font-weight: 700;
  }
  .table-caption {
    font-weight: 700;
    text-align: center;
    margin: 8px 0;
    font-size: 10pt;
  }
  .flex-spacer {
    flex-grow: 1;
  }
  .sig-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    font-size: 10pt;
  }
  .sig-table td {
    padding: 10px 4px;
    vertical-align: bottom;
  }
  .parul-badge {
    display: inline-flex;
    align-items: center;
    border: 1px solid #c00;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 15px;
  }
  .parul-red {
    background: #b91c1c;
    color: #fff;
    padding: 4px 8px;
    font-weight: 800;
    font-size: 11pt;
  }
  .naac-yellow {
    background: #facc15;
    color: #000;
    padding: 4px 8px;
    font-weight: 800;
    font-size: 10pt;
  }
  .dots-leader {
    flex-grow: 1;
    border-bottom: 1px dotted #333;
    margin: 0 6px 3px 6px;
  }
  .toc-row {
    display: flex;
    align-items: flex-end;
    margin-bottom: 4px;
    font-size: 10pt;
  }
  .toc-row.bold {
    font-weight: 700;
  }
  .diagram-container {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 15px 0;
  }
</style>
</head>
<body>
"""

    # ---------------- PAGE 1: COVER ----------------
    html += """
<!-- PAGE 1: COVER -->
<div class="page">
  <div class="border-box" style="align-items: center; justify-content: space-between; text-align: center;">
    <div style="width: 100%; text-align: left;">
      <div class="parul-badge">
        <span class="parul-red">Parul<sup>&reg;</sup><br><small style="font-size: 8pt;">University</small></span>
        <span class="naac-yellow">NAAC A++<br><small style="font-size: 6.5pt;">ACCREDITED UNIVERSITY</small></span>
      </div>
    </div>

    <h1 class="doc-title" style="margin-top: 0;">UNIFOUND &ndash; LOST AND FOUND MANAGEMENT PORTAL</h1>

    <div>
      <h2 class="report-type" style="margin-bottom: 8px;">MINOR PROJECT REPORT</h2>
      <h3 class="degree-title">Degree of Bachelor of Technology in Computer Science &amp; Engineering</h3>
      <div class="uni-title">PARUL UNIVERSITY, VADODARA, GUJARAT</div>
    </div>

    <!-- University Crest SVG -->
    <div style="margin: 15px 0;">
      <svg width="150" height="150" viewBox="0 0 200 200">
        <circle cx="100" cy="100" r="90" fill="none" stroke="#b91c1c" stroke-width="4"/>
        <circle cx="100" cy="100" r="82" fill="#fffdfa" stroke="#d97706" stroke-width="2"/>
        <path d="M50,75 Q100,45 150,75 L150,135 Q100,165 50,135 Z" fill="#fff" stroke="#b91c1c" stroke-width="3"/>
        <path d="M100,55 L100,150" stroke="#b91c1c" stroke-width="2"/>
        <circle cx="100" cy="80" r="14" fill="#f59e0b"/>
        <rect x="68" y="105" width="24" height="24" fill="#2563eb" rx="2"/>
        <rect x="108" y="105" width="24" height="24" fill="#16a34a" rx="2"/>
        <path d="M40,160 Q100,180 160,160 Q100,172 40,160" fill="#b91c1c"/>
        <text x="100" y="168" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">PARUL UNIVERSITY</text>
      </svg>
    </div>

    <div class="session-title">SESSION: 2025-2026</div>

    <div style="font-size: 10pt; line-height: 1.5;">
      <strong>Submitted By:</strong><br>
      <strong>Group Member Names :</strong> Sahil Khot (2303051240190)<br>
      Shivani Choudhary (2303051240212)<br>
      Minal Prasad (2303051240122)<br>
      Shivang Bhadwal (2303051240211)<br>
    </div>

    <div style="font-size: 10pt; line-height: 1.4; margin-top: 10px;">
      <strong>Under The Guidance of</strong><br>
      <strong>Guide Name : Mrs. Arpita Meet Vaidya</strong><br>
      <strong style="color: #8b0000; font-size: 9.5pt;">DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING</strong><br>
      <strong style="font-size: 9.5pt;">PARUL INSTITUTE OF TECHNOLOGY VADODARA, GUJARAT</strong>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 2: DECLARATION ----------------
    html += """
<!-- PAGE 2: DECLARATION -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title center-text" style="margin-top: 15px; margin-bottom: 25px;">DECLARATION</h1>
    <p>We hereby declare that the project titled <strong>“UniFound – Lost and Found Management Portal”</strong> submitted to Parul University in partial fulfillment of the requirements for the award of the degree of <strong>Bachelor of Technology (B.Tech)</strong> is an original work carried out by us under the guidance and supervision of our project guide by <strong>Mrs. Arpita Meet Vaidya</strong>, CSE Department.</p>
    <p>We further declare that this project work has not been submitted previously to any other university or institution for the award of any degree, diploma, or certification. The information presented in this report has been collected and implemented by us with proper references to the original sources wherever required.</p>
    <p>We take full responsibility for the authenticity and accuracy of the work presented in this report.</p>

    <div style="margin-top: 25px; line-height: 1.8;">
      <strong>Place: Vadodara</strong><br>
      <strong>Date: _________________</strong>
    </div>

    <div class="flex-spacer"></div>

    <table class="sig-table">
      <tr style="font-weight: bold; border-bottom: 1px solid #666;">
        <td style="width: 38%;">Name of Student</td>
        <td style="width: 32%;">Enrollment No.</td>
        <td style="width: 30%;">Signature</td>
      </tr>
      <tr>
        <td><strong>Sahil Khot</strong></td>
        <td>(2303051240190)</td>
        <td>____________________</td>
      </tr>
      <tr>
        <td><strong>Shivani Choudhary</strong></td>
        <td>(2303051240212)</td>
        <td>____________________</td>
      </tr>
      <tr>
        <td><strong>Minal Prasad</strong></td>
        <td>(2303051240122)</td>
        <td>____________________</td>
      </tr>
      <tr>
        <td><strong>Shivang Bhadwal</strong></td>
        <td>(2303051240211)</td>
        <td>____________________</td>
      </tr>
    </table>
    <div style="height: 30px;"></div>
  </div>
</div>
"""

    # ---------------- PAGE 3: ACKNOWLEDGEMENT ----------------
    html += """
<!-- PAGE 3: ACKNOWLEDGEMENT -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title center-text" style="margin-top: 15px; margin-bottom: 25px;">ACKNOWLEDGEMENT</h1>
    <p>In this semester, we have completed our project on <strong>“UniFound – Lost and Found Management Portal”</strong>. During this time, all the group members collaboratively worked on the project and learnt about the industry standards that how projects are being developed in IT Companies. We also understood the importance of teamwork while creating a project and got to learn the new technologies on which we are going to work in near future.</p>
    <p>We gratefully acknowledge for the assistance, cooperation, guidance and clarification provided by <strong>“Mrs. Arpita Meet Vaidya”</strong> during the development of our project. We would also like to thank our Head of Department <strong>Prof. Sumitra Menaria</strong> and our Principal <strong>Dr. Swapnil Parikh Sir</strong> for giving us an opportunity to develop this project. Their continuous motivation and guidance helped us overcome the different obstacles for completing the Project.</p>
    <p>We perceive this as an opportunity and a big milestone in our career development. We will strive to use gained skills and knowledge in our best possible way and we will work to improve them.</p>

    <div style="margin-top: 35px; line-height: 1.8;">
      <strong>Team Members :</strong><br>
      Sahil Khot<br>
      Shivani Choudhary<br>
      Minal Prasad<br>
      Shivang Bhadwal
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 4: CERTIFICATE ----------------
    html += """
<!-- PAGE 4: CERTIFICATE -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title center-text" style="margin-top: 15px; margin-bottom: 25px;">CERTIFICATE</h1>
    <p>This is to certify that <strong>Sahil Khot, Shivani Choudhary, Minal Prasad, Shivang Bhadwal</strong> Students of <strong>CSE VI Semester</strong> of <strong>Parul Institute of Technology, Vadodara</strong> has completed their Minor Project titled <strong>UNIFOUND - Lost and Found Management Portal</strong>, as per the syllabus and has submitted a satisfactory report on this project as a partial fulfillment towards the award of degree of <strong>Bachelor of Technology in Computer Science and Engineering</strong> under <strong>Parul University, Vadodara, Gujarat (India)</strong>.</p>

    <div style="margin: 25px 0 25px 20px; line-height: 1.9;">
      <strong>Sahil Khot [2303051240190]</strong><br>
      <strong>Shivani Choudhary [2303051240212]</strong><br>
      <strong>Minal Prasad [2303051240122]</strong><br>
      <strong>Shivang Bhadwal [2303051240211]</strong>
    </div>

    <p>Under the guidance of the project supervisor in partial fulfillment of the requirement for the award of the degree of Bachelor of Engineering.</p>

    <div class="flex-spacer"></div>

    <div style="display: flex; justify-content: space-between; margin-bottom: 40px; padding: 0 10px;">
      <div style="text-align: center;">
        ___________________________<br>
        <strong>Project Guide</strong><br>
        Mrs. Arpita Meet Vaidya
      </div>
      <div style="text-align: center;">
        ___________________________<br>
        <strong>Head of Department</strong><br>
        Prof. Sumitra Menaria
      </div>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 5: ABSTRACT (PART 1) ----------------
    html += """
<!-- PAGE 5: ABSTRACT (PART 1) -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title" style="margin-bottom: 14px;">ABSTRACT</h1>
    <p>The rapid growth of large university campuses and the increasing number of students, faculty members, and staff have created new challenges in managing lost and found items effectively. In many educational institutions, students frequently lose personal belongings such as identity cards, wallets, books, electronic devices, keys, and other valuable items. Traditionally, lost and found items are managed through manual systems where students report lost belongings to the security office or administrative department. These offices maintain physical registers or notice boards where information about lost or found items is recorded. However, such traditional approaches are inefficient, time-consuming, and often unsuccessful in reconnecting lost items with their rightful owners. Manual systems make it difficult to search for items quickly, track reports, or notify users when their belongings are found.</p>
    
    <p>To address these challenges, the <strong>UniFound &ndash; Lost and Found Management Portal</strong> has been developed as a digital platform designed specifically for university campuses. The main objective of UniFound is to simplify and streamline the process of reporting, searching, and recovering lost items through an online system. This web-based portal allows students, faculty members, and campus staff to report lost items and found items in a centralized database. By providing a digital platform, the system eliminates the need for physical registers and manual record management.</p>

    <p>The UniFound system enables users to create reports for lost or found items by entering relevant information such as item name, description, category, location where the item was lost or found, date, and contact details. Users can also upload images of the items to improve identification and matching accuracy. Once the information is submitted, the system stores it in a structured database where it can be accessed and searched by other users. If someone finds an item that matches a previously reported lost item, they can easily contact the owner through the system.</p>

    <p>The portal also provides a search feature that allows users to browse through the list of reported lost and found items. The search functionality helps users quickly locate items by filtering based on categories such as electronics, documents, accessories, or personal belongings. This significantly improves the chances of recovering lost items compared to traditional manual methods.</p>

    <p>From a technical perspective, the UniFound portal is designed using modern web development technologies. The system uses <strong>Python 3.11+ and the FastAPI framework</strong> as the programming language and architecture for backend logic and <strong>React, TypeScript, and Vite with modern CSS</strong> for developing the responsive frontend interface. The database component of the system is implemented using <strong>PostgreSQL and SQLite with SQLAlchemy 2.0 ORM</strong>, which enables efficient storage and retrieval of item records. Development tools such as <strong>Visual Studio Code, Git, and GitHub</strong> are used for coding, version control, and cloud deployments on <strong>Render and Vercel</strong>.</p>

    <p>One of the key advantages of the UniFound portal is that it provides a <strong>centralized and transparent platform for managing lost and found items within the university</strong>. Instead of relying on security offices or word-of-mouth communication, users can directly access the system and check the status of their items online. This improves accessibility and reduces the time required to locate lost belongings. Additionally, the system maintains a digital record of all reports, making it easier to track items and manage data efficiently.</p>
  </div>
</div>
"""

    # ---------------- PAGE 6: ABSTRACT (PART 2) ----------------
    html += """
<!-- PAGE 6: ABSTRACT (PART 2) -->
<div class="page">
  <div class="border-box">
    <p>Another important benefit of the system is improved communication between users. When a lost item is reported and later found by another user, the portal enables quick contact between the two parties. This increases the likelihood of successful item recovery and helps build a cooperative campus environment where students help each other.</p>
    
    <p>The UniFound portal also enhances data organization and management. Since all records are stored digitally, administrators can easily monitor reports, remove duplicate entries, and manage the overall system. The platform is scalable and can be expanded in the future to include additional features such as mobile application support, automated notifications, image recognition for item matching, and integration with campus identification systems.</p>

    <p>Despite its advantages, the system also has some limitations. The success of the platform depends on user participation and accurate reporting of lost or found items. If users do not actively use the system, the efficiency of the portal may be reduced. However, with proper awareness and adoption across the campus community, the UniFound portal can significantly improve the management of lost items.</p>

    <p>In conclusion, the <strong>UniFound &ndash; Lost and Found Management Portal</strong> offers a modern and efficient solution to the common problem of lost belongings in universities. By replacing manual reporting methods with a digital platform, the system improves accessibility, transparency, and efficiency in managing lost and found items. The portal not only helps users recover their belongings more quickly but also promotes a more organized and collaborative campus environment. With further development and integration of advanced technologies, UniFound has the potential to become a comprehensive smart campus service for lost and found management.</p>
  </div>
</div>
"""

    # ---------------- PAGE 7: LIST OF ABBREVIATIONS ----------------
    html += """
<!-- PAGE 7: LIST OF ABBREVIATIONS -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title" style="margin-bottom: 18px;">LIST OF ABBREVIATIONS</h1>
    <table class="report-table">
      <thead>
        <tr>
          <th style="width: 30%;">Abbreviation</th>
          <th style="width: 70%;">Full Form</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><strong>GUI</strong></td><td>Graphical User Interface</td></tr>
        <tr><td><strong>HTML</strong></td><td>Hyper Text Markup Language</td></tr>
        <tr><td><strong>CSS</strong></td><td>Cascading Style Sheets</td></tr>
        <tr><td><strong>JS</strong></td><td>JavaScript</td></tr>
        <tr><td><strong>TS</strong></td><td>TypeScript</td></tr>
        <tr><td><strong>DB</strong></td><td>Database</td></tr>
        <tr><td><strong>ER</strong></td><td>Entity Relationship</td></tr>
        <tr><td><strong>DFD</strong></td><td>Data Flow Diagram</td></tr>
        <tr><td><strong>UI</strong></td><td>User Interface</td></tr>
        <tr><td><strong>RAM</strong></td><td>Random Access Memory</td></tr>
        <tr><td><strong>OS</strong></td><td>Operating System</td></tr>
        <tr><td><strong>API</strong></td><td>Application Programming Interface</td></tr>
        <tr><td><strong>ASGI</strong></td><td>Asynchronous Server Gateway Interface</td></tr>
        <tr><td><strong>IDE</strong></td><td>Integrated Development Environment</td></tr>
        <tr><td><strong>SQL</strong></td><td>Structured Query Language</td></tr>
        <tr><td><strong>HTTP</strong></td><td>Hypertext Transfer Protocol</td></tr>
        <tr><td><strong>URL</strong></td><td>Uniform Resource Locator</td></tr>
        <tr><td><strong>JWT</strong></td><td>JSON Web Token</td></tr>
        <tr><td><strong>REST</strong></td><td>Representational State Transfer</td></tr>
        <tr><td><strong>ORM</strong></td><td>Object Relational Mapping</td></tr>
        <tr><td><strong>MCP</strong></td><td>Model Context Protocol</td></tr>
      </tbody>
    </table>
  </div>
</div>
"""

    # ---------------- PAGE 8: LIST OF FIGURES ----------------
    html += """
<!-- PAGE 8: LIST OF FIGURES -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title" style="margin-bottom: 18px;">LIST OF FIGURES</h1>
    <table class="report-table">
      <thead>
        <tr>
          <th style="width: 22%;">Figure No.</th>
          <th style="width: 63%;">Figure Title</th>
          <th style="width: 15%; text-align: center;">Page No.</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><strong>Fig 3.1</strong></td><td>Entity Relationship (ER) Diagram of UniFound System</td><td style="text-align: center;">15</td></tr>
        <tr><td><strong>Fig 3.2</strong></td><td>Use Case Diagram of UniFound Portal</td><td style="text-align: center;">16</td></tr>
        <tr><td><strong>Fig 3.3</strong></td><td>Data Flow Diagram (DFD &ndash; Level 0)</td><td style="text-align: center;">16</td></tr>
        <tr><td><strong>Fig 3.4</strong></td><td>Data Flow Diagram (DFD &ndash; Level 1)</td><td style="text-align: center;">17</td></tr>
        <tr><td><strong>Fig 5.1</strong></td><td>User Registration Interface</td><td style="text-align: center;">20</td></tr>
        <tr><td><strong>Fig 5.2</strong></td><td>User Login Interface</td><td style="text-align: center;">21</td></tr>
        <tr><td><strong>Fig 5.3</strong></td><td>Lost Item Reporting Page</td><td style="text-align: center;">22</td></tr>
        <tr><td><strong>Fig 5.4</strong></td><td>Found Item Reporting Page</td><td style="text-align: center;">23</td></tr>
        <tr><td><strong>Fig 5.5</strong></td><td>Admin Dashboard Interface</td><td style="text-align: center;">25</td></tr>
      </tbody>
    </table>
  </div>
</div>
"""

    # ---------------- PAGE 9: LIST OF TABLES ----------------
    html += """
<!-- PAGE 9: LIST OF TABLES -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title" style="margin-bottom: 18px;">LIST OF TABLES</h1>
    <table class="report-table">
      <thead>
        <tr>
          <th style="width: 22%;">Table No.</th>
          <th style="width: 63%;">Table Title</th>
          <th style="width: 15%; text-align: center;">Page No.</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><strong>Table 3.1</strong></td><td>Project Modules of UniFound System</td><td style="text-align: center;">13</td></tr>
        <tr><td><strong>Table 4.1</strong></td><td>Software Requirements</td><td style="text-align: center;">18</td></tr>
        <tr><td><strong>Table 4.2</strong></td><td>Hardware Requirements</td><td style="text-align: center;">19</td></tr>
        <tr><td><strong>Table 8.1</strong></td><td>Weekly Project Progress Report</td><td style="text-align: center;">30</td></tr>
      </tbody>
    </table>
  </div>
</div>
"""

    # ---------------- PAGE 10: TABLE OF CONTENTS (PART 1) ----------------
    html += """
<!-- PAGE 10: TABLE OF CONTENTS (PART 1) -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title" style="margin-bottom: 16px;">TABLE OF CONTENTS / INDEX</h1>
    
    <div class="toc-row bold"><span>FIRST PAGE (Same as Cover Page)</span><span class="dots-leader"></span><span>I</span></div>
    <div class="toc-row bold"><span>CERTIFICATE</span><span class="dots-leader"></span><span>II</span></div>
    <div class="toc-row bold"><span>DECLARATION</span><span class="dots-leader"></span><span>III</span></div>
    <div class="toc-row bold"><span>ACKNOWLEDGEMENT</span><span class="dots-leader"></span><span>IV</span></div>
    <div class="toc-row bold"><span>LIST OF FIGURES</span><span class="dots-leader"></span><span>V</span></div>
    <div class="toc-row bold"><span>LIST OF TABLES</span><span class="dots-leader"></span><span>VI</span></div>
    <div class="toc-row bold"><span>LIST OF ABBREVIATIONS</span><span class="dots-leader"></span><span>VII</span></div>
    <div class="toc-row bold"><span>ABSTRACT</span><span class="dots-leader"></span><span>VIII</span></div>
    <div class="toc-row bold"><span>INDEX</span><span class="dots-leader"></span><span>IX</span></div>
    
    <div style="height: 10px;"></div>
    <div class="toc-row bold"><span>CHAPTER I &ndash; INTRODUCTION</span><span class="dots-leader"></span><span>1</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>1.1 Overview</span><span class="dots-leader"></span><span>1</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>1.2 Problem Statement</span><span class="dots-leader"></span><span>2</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>1.3 Objective of Project</span><span class="dots-leader"></span><span>3</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>1.4 Applications / Scope</span><span class="dots-leader"></span><span>4</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>1.5 Organization of Report</span><span class="dots-leader"></span><span>5</span></div>

    <div style="height: 10px;"></div>
    <div class="toc-row bold"><span>CHAPTER II &ndash; LITERATURE SURVEY</span><span class="dots-leader"></span><span>6</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>2.1 Introduction to Existing Systems</span><span class="dots-leader"></span><span>6</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>2.2 Research on Digital Lost and Found Systems</span><span class="dots-leader"></span><span>7</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>2.3 Limitations of Existing Systems</span><span class="dots-leader"></span><span>8</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>2.4 Proposed System Advantages</span><span class="dots-leader"></span><span>9</span></div>

    <div style="height: 10px;"></div>
    <div class="toc-row bold"><span>CHAPTER III &ndash; METHODOLOGY</span><span class="dots-leader"></span><span>10</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.1 Background / Overview of Methodology</span><span class="dots-leader"></span><span>10</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.2 Project Platforms Used in Project</span><span class="dots-leader"></span><span>11</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.3 Proposed Methodology</span><span class="dots-leader"></span><span>12</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.4 Project Modules</span><span class="dots-leader"></span><span>13</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>3.5 Diagrams (ER Diagram, Use Case Diagram, DFD)</span><span class="dots-leader"></span><span>15</span></div>

    <div style="height: 10px;"></div>
    <div class="toc-row bold"><span>CHAPTER IV &ndash; SYSTEM REQUIREMENTS</span><span class="dots-leader"></span><span>18</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>4.1 Software Requirements</span><span class="dots-leader"></span><span>18</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>4.2 Hardware Requirements</span><span class="dots-leader"></span><span>19</span></div>

    <div style="height: 10px;"></div>
    <div class="toc-row bold"><span>CHAPTER V &ndash; EXPECTED OUTCOMES (WITH GUI)</span><span class="dots-leader"></span><span>20</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.1 User Registration Interface</span><span class="dots-leader"></span><span>20</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.2 User Login Interface</span><span class="dots-leader"></span><span>21</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.3 Lost Item Reporting Page</span><span class="dots-leader"></span><span>22</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.4 Found Item Reporting Page</span><span class="dots-leader"></span><span>23</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.5 Item Search and Results Page</span><span class="dots-leader"></span><span>24</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>5.6 Admin Dashboard Interface</span><span class="dots-leader"></span><span>25</span></div>
  </div>
</div>
"""

    # ---------------- PAGE 11: TABLE OF CONTENTS (PART 2) ----------------
    html += """
<!-- PAGE 11: TABLE OF CONTENTS (PART 2) -->
<div class="page">
  <div class="border-box">
    <div class="toc-row bold"><span>CHAPTER VI &ndash; CONCLUSION &amp; FUTURE SCOPE</span><span class="dots-leader"></span><span>26</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>6.1 Conclusion</span><span class="dots-leader"></span><span>26</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>6.2 Future Work</span><span class="dots-leader"></span><span>27</span></div>

    <div style="height: 12px;"></div>
    <div class="toc-row bold"><span>CHAPTER VII &ndash; REFERENCES</span><span class="dots-leader"></span><span>28</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>7.1 Books, Research Papers, Articles, and Websites</span><span class="dots-leader"></span><span>28</span></div>

    <div style="height: 12px;"></div>
    <div class="toc-row bold"><span>CHAPTER VIII &ndash; WEEKLY PROJECT REPORT</span><span class="dots-leader"></span><span>30</span></div>
    <div class="toc-row" style="padding-left: 15px;"><span>8.1 Weekly Project Progress Report</span><span class="dots-leader"></span><span>30</span></div>
  </div>
</div>
"""

    # ---------------- PAGE 12: CHAPTER 1 - INTRODUCTION (PART 1) ----------------
    html += """
<!-- PAGE 12: CHAPTER 1 - INTRODUCTION (PART 1) -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title">CHAPTER 1 &ndash; INTRODUCTION</h1>
    <h2 class="sec-title">1.1 Overview</h2>
    <p>In today's digital age, universities are becoming increasingly complex environments with thousands of students, faculty members, and staff interacting daily across multiple buildings and facilities. This large and dynamic population often results in frequent incidents of lost or misplaced personal belongings.</p>
    <p>Students carry various items such as laptops, textbooks, notebooks, mobile phones, chargers, wallets, and identification cards. Faculty members and administrative staff also carry important documents, electronic devices, and personal belongings during their daily activities.</p>
    <p>Due to the constant movement across classrooms, laboratories, libraries, cafeterias, and hostels, items are often accidentally left behind. Recovering these items can be difficult because there is no centralized system to manage lost and found information effectively.</p>
    <p>Traditional approaches such as notice boards and security registers are often inefficient and outdated. These methods require manual searching and depend heavily on human communication.</p>
    <p>To overcome these challenges, the UniFound project proposes a digital platform that simplifies the process of reporting, tracking, and recovering lost items.</p>
    <p>The UniFound system allows users to report lost items, upload images, specify locations, and search for matching items through a centralized database. The system also includes an administrative verification mechanism to ensure that recovered items are returned to the rightful owners.</p>

    <h2 class="sec-title">1.2 Problem Statement</h2>
    <p>The problem of lost items is very common in university campuses due to the large number of people moving around daily.</p>
    <p>Current methods used for managing lost items include:</p>
    <ul>
      <li>Security office registers</li>
      <li>Notice boards</li>
      <li>Social media posts</li>
      <li>Verbal communication among students</li>
    </ul>
    <p>These methods have several limitations.</p>
    <p>First, there is no centralized system to store lost and found information. Second, searching for lost items is difficult and time-consuming. Third, there is no verification process to ensure that items are returned to the correct owners. Finally, sharing personal contact information publicly may raise privacy concerns.</p>
    <p>Therefore, there is a strong need for a digital system that can efficiently manage lost and found items while ensuring security and privacy.</p>
  </div>
</div>
"""

    # ---------------- PAGE 13: CHAPTER 1 - INTRODUCTION (PART 2) ----------------
    html += """
<!-- PAGE 13: CHAPTER 1 - INTRODUCTION (PART 2) -->
<div class="page">
  <div class="border-box">
    <h2 class="sec-title">1.3 Objectives of the Project</h2>
    <p>The main objectives of the UniFound system are:</p>
    <ul>
      <li>To create a centralized platform for reporting lost and found items.</li>
      <li>To improve the efficiency of item recovery within university campuses.</li>
      <li>To allow users to upload images and descriptions of lost items.</li>
      <li>To provide search functionality for locating items quickly.</li>
      <li>To ensure user privacy through secure authentication mechanisms.</li>
      <li>To enable administrators to verify claims before returning items.</li>
    </ul>

    <h2 class="sec-title">1.4 Applications or Scope</h2>
    <p>The UniFound system can be used in multiple environments such as:</p>
    <ul>
      <li>Universities and colleges</li>
      <li>Schools and educational institutions</li>
      <li>Corporate offices</li>
      <li>Public transportation hubs</li>
      <li>Airports and railway stations</li>
    </ul>
    <p>The system can help organizations manage lost items more efficiently by providing centralized storage, easy search capabilities, and secure communication.</p>

    <h2 class="sec-title">1.5 Organization of Report</h2>
    <p>This report is structured into multiple chapters to provide a detailed explanation of the project.</p>
    <p>Chapter 1 introduces the project and discusses the problem statement and objectives.</p>
    <p>Chapter 2 reviews existing research and systems related to lost and found management.</p>
    <p>Chapter 3 explains the methodology and technologies used in the project.</p>
    <p>Chapter 4 describes the hardware and software requirements.</p>
    <p>Chapter 5 presents the expected outcomes and graphical user interface.</p>
    <p>Chapter 6 concludes the report and discusses possible future improvements.</p>
    <p>Chapter 7 lists the references used during the development of the project.</p>
  </div>
</div>
"""

    # ---------------- PAGE 14: CHAPTER 2 - LITERATURE SURVEY (PART 1) ----------------
    html += """
<!-- PAGE 14: CHAPTER 2 - LITERATURE SURVEY (PART 1) -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title">CHAPTER 2 &ndash; LITERATURE SURVEY</h1>
    <p>The literature survey is an important part of any research or software development project because it helps in understanding the existing systems, technologies, and research work related to the proposed solution. By studying previously developed systems and academic research papers, developers can identify current challenges, understand limitations of existing solutions, and propose improved systems.</p>
    <p>In the context of university environments, the management of lost and found items has traditionally been handled through manual processes. Most educational institutions rely on physical registers maintained by security offices or administrative departments where students can report lost items. When a student loses an item, they usually visit the security office and write down details such as the name of the item, location where it was lost, and their contact information. Similarly, individuals who find items may also report them to security personnel.</p>
    <p>Although this manual system provides a basic way to report lost items, it has several significant limitations. One major drawback is the lack of a centralized and easily searchable database. Since the records are maintained manually in physical registers, searching for matching lost and found items becomes a time-consuming task. Students may have to visit multiple departments or check notice boards in different buildings to find information about their lost belongings. As a result, many lost items remain unclaimed even when they have been found.</p>
    <p>Another common method used in universities is the use of physical notice boards where students post handwritten notes describing lost items. While this method allows information to be shared publicly, it is highly inefficient. Notices can be removed, damaged, or overlooked by other students. In addition, notice boards are typically limited to specific locations, meaning that students who do not frequently visit those areas may never see the information.</p>
    <p>With the rapid advancement of digital technologies and the widespread use of the internet, several institutions have begun exploring web-based solutions for lost and found management. Web-based platforms provide a centralized system where users can submit reports about lost or found items. These platforms allow users to upload item descriptions, images, and contact information, which can then be stored in a database and accessed by other users.</p>
    <p>Several existing web-based lost and found systems offer basic functionalities such as item posting, keyword search, and filtering based on categories. For example, some platforms allow users to search for items using keywords such as &ldquo;wallet,&rdquo; &ldquo;mobile phone,&rdquo; or &ldquo;laptop.&rdquo; These features significantly improve the efficiency of the search process compared to manual methods.</p>
    <p>In addition to web portals, mobile applications for lost and found management have also been developed. These applications allow users to report lost items instantly using their smartphones. Mobile applications offer several advantages such as real-time notifications, location tracking, and easy access to information.</p>
  </div>
</div>
"""

    # ---------------- PAGE 15: CHAPTER 2 - LITERATURE SURVEY (PART 2) ----------------
    html += """
<!-- PAGE 15: CHAPTER 2 - LITERATURE SURVEY (PART 2) -->
<div class="page">
  <div class="border-box">
    <p>images of found items using image processing techniques. This feature is particularly useful when users are unsure about the exact description of the item.</p>
    <p>Another important feature introduced in some digital platforms is location-based reporting. Using technologies such as GPS, map APIs, and location tagging, users can mark the exact location where an item was lost or found. This information helps others identify possible locations where the item might be recovered.</p>
    <p>Despite these technological advancements, many existing systems still face several limitations. One major issue is the <strong>lack of secure authentication mechanisms</strong>. Some platforms allow anonymous posting of lost and found items, which can lead to misuse of the system. Without proper user verification, it becomes difficult to ensure that items are returned to their rightful owners.</p>
    <p>Another limitation of existing systems is <strong>poor privacy protection</strong>. Many platforms require users to share personal contact information such as phone numbers and email addresses publicly. This can create privacy risks and may discourage users from reporting lost items.</p>
    <p>In addition, some existing systems suffer from <strong>poor scalability and limited database management capabilities</strong>. As the number of users increases, these systems may struggle to handle large volumes of data efficiently. This can lead to slow performance and reduced reliability.</p>
    <p>User interface design is another challenge faced by many existing platforms. Some systems have complex interfaces that are difficult to navigate, especially for users who are not familiar with digital platforms. A poorly designed interface can discourage users from actively participating in the system.</p>
    <p>To overcome these limitations, modern lost and found systems are increasingly incorporating <strong>secure authentication, cloud-based databases, and user-friendly interfaces</strong>. Technologies such as <strong>JSON Web Tokens (JWT)</strong> are widely used for authentication, ensuring that only authorized users can access system features.</p>
    <p>Cloud computing platforms also play an important role in modern web applications. By hosting applications on cloud platforms, developers can ensure scalability, reliability, and accessibility from different locations.</p>
    <p>The <strong>UniFound &ndash; Lost and Found Management Portal</strong> builds upon these technological advancements to provide a more efficient and secure solution for university campuses. Unlike traditional manual systems, UniFound offers a centralized digital platform where users can easily report lost or found items.</p>
    <p>The system integrates <strong>secure user authentication, centralized database storage, and location-based reporting features</strong>. These features allow users to search for items quickly and submit claims in a secure manner.</p>
    <p>Another important improvement introduced by the UniFound system is <strong>administrative verification</strong>. In this process, administrators review claim requests before approving item recovery. This helps ensure that items are returned only to their rightful owners and prevents fraudulent claims.</p>
    <p>Furthermore, the system focuses on <strong>privacy protection</strong> by avoiding the public display of personal contact information. Instead, communication between users is handled through secure claim requests and administrative approval.</p>
  </div>
</div>
"""

    # ---------------- PAGE 16: CHAPTER 2 - LITERATURE SURVEY (PART 3) ----------------
    html += """
<!-- PAGE 16: CHAPTER 2 - LITERATURE SURVEY (PART 3) -->
<div class="page">
  <div class="border-box">
    <p>Overall, the literature survey highlights the importance of digital solutions for managing lost and found items in modern university environments. While several systems have been developed in the past, many of them lack important features such as security, privacy protection, and scalability.</p>
    <p>The UniFound system aims to address these challenges by combining modern web technologies, secure authentication mechanisms, and user-friendly interfaces to create a reliable and efficient lost and found management platform.</p>
  </div>
</div>
"""

    # ---------------- PAGE 17: CHAPTER 3 - METHODOLOGY (PART 1) ----------------
    html += """
<!-- PAGE 17: CHAPTER 3 - METHODOLOGY (PART 1) -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title">CHAPTER 3 &ndash; METHODOLOGY</h1>
    <h2 class="sec-title">3.1 Background / Overview of Methodology</h2>
    <p>Methodology refers to the systematic approach used for designing, developing, and implementing the proposed system. It explains how the project was developed step by step and how different components of the system interact with each other.</p>
    <p>In the case of the UniFound &ndash; Lost and Found Management Portal, the methodology focuses on developing a web-based platform that enables students and staff members to report, search, and recover lost items efficiently within a university campus. The development of this system aims to replace traditional manual methods of reporting lost items with a more efficient digital solution.</p>
    <p>Traditional systems used in universities often rely on manual processes such as maintaining registers or posting notices on bulletin boards. These approaches are inefficient because they require manual searching, are prone to human errors, and cannot provide real-time updates. As a result, many lost items remain unclaimed even when they have been found.</p>
    <p>To address these challenges, the UniFound system follows a structured software development methodology that includes several phases such as requirement analysis, system design, development, testing, and implementation.</p>
    <p><strong>The development of the UniFound portal focuses on the following key objectives:</strong></p>
    <ul>
      <li><strong>Creating a centralized digital platform for managing lost and found items</strong></li>
      <li><strong>Providing secure user authentication to ensure system reliability</strong></li>
      <li><strong>Allowing users to report lost and found items easily</strong></li>
      <li><strong>Enabling efficient searching and matching of items</strong></li>
      <li><strong>Ensuring data privacy and security for users</strong></li>
    </ul>
    <p>The system follows a modular architecture, where each functionality is divided into separate modules such as user authentication, item reporting, search functionality, and administrative management. This modular approach makes the system easier to maintain and upgrade in the future.</p>
    <p>The UniFound system is developed using modern web technologies, allowing it to be accessible through web browsers on different devices such as laptops, tablets, and smartphones.</p>
  </div>
</div>
"""

    # ---------------- PAGE 18: CHAPTER 3 - METHODOLOGY (PART 2) ----------------
    html += """
<!-- PAGE 18: CHAPTER 3 - METHODOLOGY (PART 2) -->
<div class="page">
  <div class="border-box">
    <table class="report-table">
      <thead>
        <tr>
          <th style="width: 28%;">Module Name</th>
          <th style="width: 72%;">Description</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>User Registration Module</strong></td>
          <td>Allows new users to create an account in the UniFound system by providing details such as name, email, and password.</td>
        </tr>
        <tr>
          <td><strong>User Login Module</strong></td>
          <td>Authenticates registered users so they can securely access the system and perform actions.</td>
        </tr>
        <tr>
          <td><strong>Lost Item Reporting Module</strong></td>
          <td>Enables users to report items they have lost by entering details like item name, description, location, and date.</td>
        </tr>
        <tr>
          <td><strong>Found Item Reporting Module</strong></td>
          <td>Allows users to report items they have found so the rightful owner can claim them.</td>
        </tr>
        <tr>
          <td><strong>Item Search Module</strong></td>
          <td>Provides search functionality to find lost or found items based on category, keywords, or location.</td>
        </tr>
        <tr>
          <td><strong>Claim Request Module</strong></td>
          <td>Allows users to request ownership of a found item and communicate with the person who reported it.</td>
        </tr>
        <tr>
          <td><strong>Admin Management Module</strong></td>
          <td>Allows administrators to monitor the system, manage reports, and verify claim requests.</td>
        </tr>
      </tbody>
    </table>
    <div class="table-caption">Table 3.1 &ndash; Project Modules of UniFound System</div>

    <h2 class="sec-title" style="margin-top: 15px;">3.2 Project Platforms Used in the Project</h2>
    <p><strong>The UniFound system is developed using several software technologies and development platforms that enable efficient system functionality and user interaction.</strong></p>
    <p><strong>Frontend Technologies</strong></p>
    <p>The frontend of the system refers to the user interface that allows users to interact with the platform. The frontend is responsible for displaying information, accepting user inputs, and ensuring smooth navigation across the platform.</p>
    <p>The following technologies are used for frontend development:</p>
    <p><strong>HTML (HyperText Markup Language)</strong><br>
    HTML is used to create the structure of web pages. It defines elements such as headings, paragraphs, forms, buttons, and input fields that allow users to interact with the system.</p>
  </div>
</div>
"""

    # ---------------- PAGE 19: CHAPTER 3 - METHODOLOGY (PART 3) ----------------
    html += """
<!-- PAGE 19: CHAPTER 3 - METHODOLOGY (PART 3) -->
<div class="page">
  <div class="border-box">
    <p><strong>CSS (Cascading Style Sheets)</strong><br>
    CSS is used to design and style the web pages. It controls visual aspects such as colors, fonts, layouts, spacing, and responsiveness. CSS helps create a user-friendly interface that improves the overall user experience.</p>
    
    <p><strong>React and TypeScript Framework</strong><br>
    React 18 with TypeScript is used for developing a dynamic, component-driven single page application (SPA). It provides structured state management, responsive glassmorphic cards, intuitive navigation bars, forms, buttons, and modal dialogs. React ensures that the UniFound platform looks professional and works seamlessly on different screen sizes.</p>

    <h2 class="sec-title">Backend Technologies</h2>
    <p><strong>The backend is responsible for handling business logic, managing user requests, processing data, and interacting with the database.</strong></p>
    
    <p><strong>FastAPI Framework</strong><br>
    FastAPI is a high-performance Python web framework used for rapid, asynchronous REST API development. It provides several built-in features such as OAuth2 authentication systems, Pydantic data validation, database integration via SQLAlchemy, and security mechanisms.</p>
    <p>FastAPI separates application logic into modular routers, schemas, models, and service layers, making the system organized, robust, and easy to maintain.</p>
    <p>The main advantages of using FastAPI include:</p>
    <ul>
      <li>Secure authentication system with JWT</li>
      <li>Built-in database management via SQLAlchemy ORM</li>
      <li>Fast asynchronous development process and high throughput</li>
      <li>High scalability and automatic Swagger API documentation</li>
      <li>Strong community support and modern Python type hinting</li>
    </ul>

    <h2 class="sec-title">Database Technology</h2>
    <p><strong>PostgreSQL and SQLite Database</strong><br>
    PostgreSQL is used in production (with SQLite in development) as the database for storing all system data such as user accounts, lost item reports, found item reports, and claim requests.</p>
    <p>The database stores information such as:</p>
    <ul>
      <li>User details (name, email, hashed password)</li>
      <li>Lost item reports</li>
      <li>Found item reports</li>
      <li>Item descriptions</li>
    </ul>
  </div>
</div>
"""

    # ---------------- PAGE 20: CHAPTER 3 - METHODOLOGY (PART 4) ----------------
    html += """
<!-- PAGE 20: CHAPTER 3 - METHODOLOGY (PART 4) -->
<div class="page">
  <div class="border-box">
    <ul>
      <li>Upload timestamps</li>
      <li>Claim request details</li>
    </ul>
    <p>SQLite is lightweight, easy to integrate during development, while PostgreSQL provides robust concurrency, transactions, and scaling for production cloud deployment.</p>

    <h2 class="sec-title">Development Tools</h2>
    <p><strong>The following tools were used during development:</strong></p>
    <p><strong>Visual Studio Code (VS Code)</strong><br>
    A powerful code editor used for writing and managing the project code.</p>
    <p><strong>GitHub</strong><br>
    Used for version control and project collaboration.</p>
    <p><strong>Web Browser (Chrome / Edge)</strong><br>
    Used for testing and running the application during development.</p>

    <h2 class="sec-title">3.3 Proposed Methodology</h2>
    <p><strong>The proposed methodology for the UniFound system focuses on creating an efficient and secure digital platform for managing lost and found items within a university environment.</strong></p>
    <p><strong>The system operates through a series of structured steps that allow users to report lost items, search for found items, and submit claims for item recovery.</strong></p>
    <p><strong>The main steps of the proposed methodology are described below.</strong></p>
    <p><strong>User Registration</strong><br>
    The first step in using the UniFound system is user registration. Students and staff members must create an account by providing basic information such as name, email address, and password. The registration system ensures that only verified users can access the platform.</p>
    <p><strong>User Authentication</strong><br>
    After registration, users can log in to the system using their credentials. The secure authentication system ensures secure login and protects user accounts from unauthorized access.</p>
    <p><strong>Reporting Lost Items</strong><br>
    Users who lose an item can report it through the platform by filling out a form containing the following information:</p>
    <ul>
      <li>Item name</li>
      <li>Item description</li>
      <li>Category (electronics, accessories, documents, etc.)</li>
      <li>Location where the item was lost</li>
    </ul>
  </div>
</div>
"""

    # ---------------- PAGE 21: CHAPTER 3 - METHODOLOGY (PART 5) ----------------
    html += """
<!-- PAGE 21: CHAPTER 3 - METHODOLOGY (PART 5) -->
<div class="page">
  <div class="border-box">
    <ul>
      <li>Date of loss</li>
      <li>Optional image upload</li>
    </ul>
    <p>This information is stored in the database and becomes searchable by other users.</p>

    <p><strong>Reporting Found Items</strong><br>
    Users who find an item can also report it through the system by providing similar details such as item description, location, and image.</p>

    <p><strong>Search and Matching</strong><br>
    The system provides a search feature that allows users to look for items using keywords, categories, or locations. This functionality helps users quickly identify possible matches between lost and found items.</p>

    <p><strong>Claim Request</strong><br>
    If a user identifies a matching item, they can submit a claim request through the platform. The claim request is then reviewed by the system administrator.</p>

    <p><strong>Administrator Verification</strong><br>
    The administrator reviews claim requests and verifies ownership before approving item recovery. This process ensures that items are returned only to their rightful owners.</p>

    <h2 class="sec-title">3.4 Project Modules</h2>
    <p><strong>The UniFound system consists of several modules that work together to provide complete functionality.</strong></p>
    <p><strong>User Module</strong><br>
    The user module allows students and staff members to interact with the system. It includes functionalities such as registration, login, reporting items, searching for items, and submitting claim requests.</p>
    <p><strong>Authentication Module</strong><br>
    This module handles user login, logout, and account security using a token-based authentication system.</p>
    <p><strong>Lost Item Module</strong><br>
    This module allows users to submit reports for items they have lost. The system stores the information in the database and displays it on the platform.</p>
    <p><strong>Found Item Module</strong><br>
    Users who find items can report them through this module, helping others recover their belongings.</p>
  </div>
</div>
"""

    # ---------------- PAGE 22: CHAPTER 3 - METHODOLOGY (PART 6) & ER DIAGRAM ----------------
    html += """
<!-- PAGE 22: CHAPTER 3 - METHODOLOGY (PART 6) & ER DIAGRAM -->
<div class="page">
  <div class="border-box">
    <p><strong>Search Module</strong><br>
    This module allows users to search for lost or found items using keywords, filters, and categories.</p>
    <p><strong>Admin Module</strong><br>
    The admin module allows administrators to manage the entire system. Administrators can review reports, verify claim requests, and remove invalid entries.</p>

    <h2 class="sec-title">3.5 Diagrams (ER Diagram, Use Case Diagram, DFD)</h2>
    <p>System diagrams help visualize the structure and functionality of the application.</p>
    <p><strong>Entity Relationship (ER) Diagram</strong><br>
    The ER diagram represents the relationships between different entities in the database.</p>
    <p>Main entities in the UniFound system include:</p>
    <ul>
      <li><strong>User:</strong> Stores user information such as name, email, and password.</li>
      <li><strong>Lost Item:</strong> Stores details of items reported as lost.</li>
      <li><strong>Found Item:</strong> Stores details of items reported as found.</li>
      <li><strong>Claim Request:</strong> Represents requests made by users to claim found items.</li>
    </ul>
    <p>Relationships between these entities allow the system to manage lost and found data efficiently.</p>

    <div class="diagram-container">
      <svg width="480" height="260" viewBox="0 0 520 280">
        <!-- ER Diagram SVG -->
        <rect x="20" y="20" width="110" height="70" fill="#3b82f6" rx="4" opacity="0.9"/>
        <text x="75" y="42" fill="#fff" font-weight="bold" text-anchor="middle" font-size="11">Lost Item</text>
        <text x="75" y="58" fill="#fff" text-anchor="middle" font-size="8.5">• ItemID • ItemName</text>
        <text x="75" y="72" fill="#fff" text-anchor="middle" font-size="8.5">• Category • LostDate</text>

        <rect x="390" y="20" width="110" height="70" fill="#3b82f6" rx="4" opacity="0.9"/>
        <text x="445" y="42" fill="#fff" font-weight="bold" text-anchor="middle" font-size="11">Found Item</text>
        <text x="445" y="58" fill="#fff" text-anchor="middle" font-size="8.5">• FoundID • ItemName</text>
        <text x="445" y="72" fill="#fff" text-anchor="middle" font-size="8.5">• Location • FoundDate</text>

        <rect x="20" y="180" width="110" height="70" fill="#3b82f6" rx="4" opacity="0.9"/>
        <text x="75" y="202" fill="#fff" font-weight="bold" text-anchor="middle" font-size="11">User</text>
        <text x="75" y="218" fill="#fff" text-anchor="middle" font-size="8.5">• UserID • Name</text>
        <text x="75" y="232" fill="#fff" text-anchor="middle" font-size="8.5">• Email • Password</text>

        <rect x="390" y="180" width="110" height="70" fill="#3b82f6" rx="4" opacity="0.9"/>
        <text x="445" y="202" fill="#fff" font-weight="bold" text-anchor="middle" font-size="11">Claim</text>
        <text x="445" y="218" fill="#fff" text-anchor="middle" font-size="8.5">• ClaimID • UserID</text>
        <text x="445" y="232" fill="#fff" text-anchor="middle" font-size="8.5">• ItemID • Status</text>

        <rect x="210" y="180" width="100" height="70" fill="#0284c7" rx="4" opacity="0.9"/>
        <text x="260" y="205" fill="#fff" font-weight="bold" text-anchor="middle" font-size="11">Admin</text>
        <text x="260" y="222" fill="#fff" text-anchor="middle" font-size="8.5">• AdminID • Role</text>

        <!-- Connecting Lines & Diamonds -->
        <polygon points="75,125 100,140 75,155 50,140" fill="#f59e0b" stroke="#333"/>
        <text x="75" y="143" fill="#000" font-size="8" text-anchor="middle" font-weight="bold">Reports</text>
        <line x1="75" y1="90" x2="75" y2="125" stroke="#333" stroke-width="1.5"/>
        <line x1="75" y1="155" x2="75" y2="180" stroke="#333" stroke-width="1.5"/>

        <polygon points="445,125 470,140 445,155 420,140" fill="#f59e0b" stroke="#333"/>
        <text x="445" y="143" fill="#000" font-size="8" text-anchor="middle" font-weight="bold">Manages</text>
        <line x1="445" y1="90" x2="445" y2="125" stroke="#333" stroke-width="1.5"/>
        <line x1="445" y1="155" x2="445" y2="180" stroke="#333" stroke-width="1.5"/>

        <line x1="130" y1="215" x2="210" y2="215" stroke="#333" stroke-width="1.5"/>
        <line x1="310" y1="215" x2="390" y2="215" stroke="#333" stroke-width="1.5"/>
        <line x1="260" y1="180" x2="445" y2="90" stroke="#333" stroke-width="1.5" stroke-dasharray="3,3"/>
      </svg>
    </div>
    <div class="table-caption">Fig 3.1 &ndash; Entity Relationship (ER) Diagram of UniFound System</div>
  </div>
</div>
"""

    # ---------------- PAGE 23: USE CASE DIAGRAM ----------------
    html += """
<!-- PAGE 23: USE CASE DIAGRAM -->
<div class="page">
  <div class="border-box">
    <p><strong>The use case diagram shows interactions between system users and system functionalities.</strong></p>
    <p>Main actors include:</p>
    <div style="display: flex; justify-content: space-between;">
      <div style="width: 48%;">
        <strong>User</strong>
        <ul>
          <li>Register account</li>
          <li>Login to system</li>
          <li>Report lost item</li>
          <li>Report found item</li>
          <li>Search items</li>
          <li>Submit claim request</li>
        </ul>
      </div>
      <div style="width: 48%;">
        <strong>Administrator</strong>
        <ul>
          <li>Manage item reports</li>
          <li>Verify claim requests</li>
          <li>Approve or reject claims</li>
          <li>Manage system database</li>
        </ul>
      </div>
    </div>

    <div class="diagram-container" style="margin-top: 25px;">
      <svg width="480" height="340" viewBox="0 0 520 360">
        <!-- Use Case SVG -->
        <!-- User Stick Figure -->
        <circle cx="50" cy="140" r="14" fill="none" stroke="#222" stroke-width="2"/>
        <line x1="50" y1="154" x2="50" y2="210" stroke="#222" stroke-width="2"/>
        <line x1="25" y1="175" x2="75" y2="175" stroke="#222" stroke-width="2"/>
        <line x1="50" y1="210" x2="30" y2="250" stroke="#222" stroke-width="2"/>
        <line x1="50" y1="210" x2="70" y2="250" stroke="#222" stroke-width="2"/>
        <text x="50" y="275" font-weight="bold" text-anchor="middle" font-size="12">User</text>

        <!-- Admin Stick Figure -->
        <circle cx="470" cy="140" r="14" fill="none" stroke="#222" stroke-width="2"/>
        <line x1="470" y1="154" x2="470" y2="210" stroke="#222" stroke-width="2"/>
        <line x1="445" y1="175" x2="495" y2="175" stroke="#222" stroke-width="2"/>
        <line x1="470" y1="210" x2="450" y2="250" stroke="#222" stroke-width="2"/>
        <line x1="470" y1="210" x2="490" y2="250" stroke="#222" stroke-width="2"/>
        <text x="470" y="275" font-weight="bold" text-anchor="middle" font-size="12">Admin</text>

        <!-- Use Cases Ovals -->
        <ellipse cx="260" cy="35" rx="85" ry="18" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5"/>
        <text x="260" y="39" text-anchor="middle" font-size="10" font-weight="bold">Register Account</text>

        <ellipse cx="260" cy="85" rx="85" ry="18" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5"/>
        <text x="260" y="89" text-anchor="middle" font-size="10" font-weight="bold">Login</text>

        <ellipse cx="260" cy="135" rx="85" ry="18" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5"/>
        <text x="260" y="139" text-anchor="middle" font-size="10" font-weight="bold">Report Lost Item</text>

        <ellipse cx="260" cy="185" rx="85" ry="18" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5"/>
        <text x="260" y="189" text-anchor="middle" font-size="10" font-weight="bold">Report Found Item</text>

        <ellipse cx="260" cy="235" rx="85" ry="18" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5"/>
        <text x="260" y="239" text-anchor="middle" font-size="10" font-weight="bold">Search Items</text>

        <ellipse cx="260" cy="285" rx="85" ry="18" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5"/>
        <text x="260" y="289" text-anchor="middle" font-size="10" font-weight="bold">Claim Item</text>

        <ellipse cx="260" cy="335" rx="85" ry="18" fill="#fecdd3" stroke="#e11d48" stroke-width="1.5"/>
        <text x="260" y="339" text-anchor="middle" font-size="10" font-weight="bold">Verify Claims &amp; Analytics</text>

        <!-- Lines -->
        <line x1="75" y1="160" x2="175" y2="35" stroke="#666"/>
        <line x1="75" y1="160" x2="175" y2="85" stroke="#666"/>
        <line x1="75" y1="160" x2="175" y2="135" stroke="#666"/>
        <line x1="75" y1="160" x2="175" y2="185" stroke="#666"/>
        <line x1="75" y1="160" x2="175" y2="235" stroke="#666"/>
        <line x1="75" y1="160" x2="175" y2="285" stroke="#666"/>

        <line x1="445" y1="160" x2="345" y2="85" stroke="#666"/>
        <line x1="445" y1="160" x2="345" y2="135" stroke="#666"/>
        <line x1="445" y1="160" x2="345" y2="185" stroke="#666"/>
        <line x1="445" y1="160" x2="345" y2="235" stroke="#666"/>
        <line x1="445" y1="160" x2="345" y2="285" stroke="#666"/>
        <line x1="445" y1="160" x2="345" y2="335" stroke="#e11d48" stroke-width="1.5"/>
      </svg>
    </div>
    <div class="table-caption">Fig 3.2 &ndash; Use Case Diagram of UniFound Portal</div>
  </div>
</div>
"""

    # ---------------- PAGE 24: DFD LEVEL 0 ----------------
    html += """
<!-- PAGE 24: DFD LEVEL 0 -->
<div class="page">
  <div class="border-box">
    <h2 class="sec-title">Data Flow Diagram (DFD)</h2>
    <p>The data flow diagram shows how data moves through the system.</p>
    <p><strong>Level 0 DFD (Context Diagram)</strong></p>
    <p>The UniFound system acts as the central process that interacts with users and administrators.</p>
    <p><strong>Inputs include:</strong></p>
    <ul>
      <li>Lost item reports</li>
      <li>Found item reports</li>
      <li>Claim requests</li>
    </ul>
    <p><strong>Outputs include:</strong></p>
    <ul>
      <li>Search results</li>
      <li>Claim approval notifications</li>
    </ul>

    <div class="diagram-container" style="margin-top: 25px;">
      <svg width="480" height="300" viewBox="0 0 520 320">
        <!-- DFD Level 0 SVG -->
        <rect x="20" y="80" width="100" height="50" rx="25" fill="#bae6fd" stroke="#0284c7" stroke-width="2"/>
        <text x="70" y="110" font-weight="bold" text-anchor="middle" font-size="12">User</text>

        <rect x="400" y="80" width="100" height="50" rx="25" fill="#fde68a" stroke="#d97706" stroke-width="2"/>
        <text x="450" y="110" font-weight="bold" text-anchor="middle" font-size="12">Admin</text>

        <circle cx="260" cy="105" r="55" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>
        <text x="260" y="98" fill="#fff" font-weight="bold" text-anchor="middle" font-size="12">0</text>
        <text x="260" y="116" fill="#fff" font-weight="bold" text-anchor="middle" font-size="11">UniFound</text>
        <text x="260" y="130" fill="#fff" font-weight="bold" text-anchor="middle" font-size="10">System</text>

        <rect x="190" y="240" width="140" height="40" fill="#f97316" rx="4" stroke="#c2410c" stroke-width="2"/>
        <text x="260" y="265" fill="#fff" font-weight="bold" text-anchor="middle" font-size="10.5">Lost &amp; Found Database</text>

        <!-- Arrows -->
        <path d="M120,95 L205,95" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
        <text x="160" y="88" font-size="8" text-anchor="middle">Reports / Claims</text>

        <path d="M205,115 L120,115" stroke="#333" stroke-width="1.5"/>
        <text x="160" y="127" font-size="8" text-anchor="middle">Results / Alerts</text>

        <path d="M400,95 L315,95" stroke="#333" stroke-width="1.5"/>
        <text x="360" y="88" font-size="8" text-anchor="middle">Verifications</text>

        <path d="M315,115 L400,115" stroke="#333" stroke-width="1.5"/>
        <text x="360" y="127" font-size="8" text-anchor="middle">Pending Queues</text>

        <path d="M260,160 L260,240" stroke="#333" stroke-width="2"/>
        <text x="270" y="200" font-size="8.5">Read/Write Data</text>
      </svg>
    </div>
    <div class="table-caption">Fig 3.3 &ndash; Data Flow Diagram (DFD &ndash; Level 0)</div>
  </div>
</div>
"""

    # ---------------- PAGE 25: DFD LEVEL 1 ----------------
    html += """
<!-- PAGE 25: DFD LEVEL 1 -->
<div class="page">
  <div class="border-box">
    <h2 class="sec-title">Level 1 DFD</h2>
    <p>The system is divided into multiple processes such as:</p>
    <ul>
      <li>User authentication</li>
      <li>Item reporting</li>
      <li>Item search</li>
      <li>Claim verification</li>
    </ul>
    <p>Each process interacts with the system database to store and retrieve data.</p>

    <div class="diagram-container" style="margin-top: 15px;">
      <svg width="490" height="340" viewBox="0 0 530 360">
        <!-- DFD Level 1 SVG -->
        <rect x="15" y="20" width="115" height="35" rx="17" fill="#bae6fd" stroke="#0284c7"/>
        <text x="72" y="42" font-size="9" font-weight="bold" text-anchor="middle">1.0 Report Lost Item</text>

        <rect x="15" y="70" width="115" height="35" rx="17" fill="#bae6fd" stroke="#0284c7"/>
        <text x="72" y="92" font-size="9" font-weight="bold" text-anchor="middle">2.0 Report Found Item</text>

        <rect x="15" y="120" width="115" height="35" rx="17" fill="#bae6fd" stroke="#0284c7"/>
        <text x="72" y="142" font-size="9" font-weight="bold" text-anchor="middle">3.0 Search Items</text>

        <rect x="200" y="65" width="110" height="70" rx="6" fill="#3b82f6" stroke="#1d4ed8"/>
        <text x="255" y="95" fill="#fff" font-weight="bold" text-anchor="middle" font-size="11">0</text>
        <text x="255" y="112" fill="#fff" font-weight="bold" text-anchor="middle" font-size="10">UniFound System</text>

        <rect x="380" y="20" width="115" height="35" rx="17" fill="#bbf7d0" stroke="#16a34a"/>
        <text x="437" y="42" font-size="9" font-weight="bold" text-anchor="middle">5.0 Process Claims</text>

        <rect x="400" y="85" width="90" height="40" rx="20" fill="#fde68a" stroke="#d97706"/>
        <text x="445" y="110" font-weight="bold" text-anchor="middle" font-size="11">Admin</text>

        <rect x="150" y="200" width="130" height="35" rx="17" fill="#fed7aa" stroke="#ea580c"/>
        <text x="215" y="222" font-size="9" font-weight="bold" text-anchor="middle">4.0 User Management</text>

        <!-- Databases -->
        <rect x="20" y="275" width="120" height="40" fill="#64748b" rx="4"/>
        <text x="80" y="300" fill="#fff" font-weight="bold" text-anchor="middle" font-size="9.5">User Database</text>

        <rect x="370" y="275" width="130" height="40" fill="#f97316" rx="4"/>
        <text x="435" y="300" fill="#fff" font-weight="bold" text-anchor="middle" font-size="9.5">Lost &amp; Found DB</text>

        <!-- Lines -->
        <line x1="130" y1="37" x2="200" y2="85" stroke="#333"/>
        <line x1="130" y1="87" x2="200" y2="95" stroke="#333"/>
        <line x1="130" y1="137" x2="200" y2="115" stroke="#333"/>
        <line x1="310" y1="85" x2="380" y2="40" stroke="#333"/>
        <line x1="445" y1="55" x2="445" y2="85" stroke="#333"/>
        <line x1="255" y1="135" x2="215" y2="200" stroke="#333"/>
        <line x1="215" y1="235" x2="80" y2="275" stroke="#333"/>
        <line x1="280" y1="220" x2="370" y2="285" stroke="#333"/>
        <line x1="445" y1="125" x2="445" y2="275" stroke="#333"/>
      </svg>
    </div>
    <div class="table-caption">Fig 3.4 &ndash; Data Flow Diagram (DFD &ndash; Level 1)</div>
    <p style="margin-top: 15px; font-weight: bold;">This structured methodology ensures that the UniFound system is organized, secure, and efficient for managing lost and found items in a university environment.</p>
  </div>
</div>
"""

    # ---------------- PAGE 26: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 1) ----------------
    html += """
<!-- PAGE 26: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 1) -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title">CHAPTER 4 &ndash; SYSTEM REQUIREMENTS</h1>
    <p>System requirements describe the hardware and software components required to develop, deploy, and run the proposed system successfully. These requirements ensure that the UniFound platform functions smoothly and efficiently without performance issues.</p>
    <p>The UniFound &ndash; Lost and Found Management Portal is a <strong>web-based application</strong>, which means it can be accessed through a web browser from different devices connected to the internet. Therefore, the system requirements focus on providing the necessary environment for both development and user interaction.</p>
    <p>The system requirements are divided into two main categories:</p>
    <ul>
      <li>Software Requirements</li>
      <li>Hardware Requirements</li>
    </ul>

    <h2 class="sec-title">4.1 Software Requirements</h2>
    <p>Software requirements refer to the programs, frameworks, and technologies used to design, develop, and run the UniFound system. These tools are essential for building the application's frontend interface, backend logic, and database management.</p>
    <p>The main software requirements for the UniFound system are described below.</p>

    <h2 class="sec-title">Operating System</h2>
    <p>The system can run on modern operating systems such as <strong>Windows or Linux</strong>.</p>
    <p>The development and testing of the UniFound portal can be performed on Windows-based systems as well as Linux distributions such as Ubuntu. Both operating systems provide the necessary environment for Python development and web application hosting.</p>
    <p>Operating systems play an important role in managing system resources, running development tools, and supporting programming frameworks. They provide the platform on which the application and its dependencies operate.</p>
    <p>Advantages of using Windows or Linux include:</p>
    <ul>
      <li>Support for Python development environments</li>
      <li>Compatibility with modern web browsers</li>
      <li>Availability of development tools such as VS Code and Git</li>
      <li>Efficient file and process management</li>
    </ul>
    <p>Linux is often preferred for deployment because of its stability and security, while Windows is commonly used during development due to its user-friendly environment.</p>

    <h2 class="sec-title">Programming Language &ndash; Python</h2>
    <p>Python is used as the primary programming language for developing the backend of the UniFound system.</p>
  </div>
</div>
"""

    # ---------------- PAGE 27: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 2) ----------------
    html += """
<!-- PAGE 27: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 2) -->
<div class="page">
  <div class="border-box">
    <p>Python is a high-level, interpreted programming language that is widely used in web development, data analysis, artificial intelligence, and automation. It provides simple syntax, which makes it easy to write and maintain code.</p>
    <p>Python offers several advantages for web application development:</p>
    <ul>
      <li>Easy to learn and use</li>
      <li>Large community support</li>
      <li>Extensive libraries and frameworks</li>
      <li>High scalability and flexibility</li>
    </ul>
    <p>In the UniFound system, Python is used to handle backend operations such as:</p>
    <ul>
      <li>Processing user requests</li>
      <li>Managing item reports</li>
      <li>Handling authentication and login systems</li>
      <li>Interacting with the database</li>
      <li>Implementing search functionality</li>
    </ul>
    <p>Python ensures that the system remains efficient, secure, and easy to maintain.</p>

    <h2 class="sec-title">Frontend Technologies &ndash; HTML, CSS, JavaScript, React, TypeScript</h2>
    <p>The frontend of the system is responsible for displaying the user interface and enabling interaction between users and the application.</p>
    <p><strong>HTML (HyperText Markup Language)</strong><br>
    HTML is used to structure the web pages of the UniFound portal. It defines the layout of the pages and organizes elements such as headings, forms, buttons, tables, and input fields.</p>
    <p>For example, HTML is used to create pages such as:</p>
    <ul>
      <li>User registration page</li>
      <li>Login page</li>
      <li>Lost item report form</li>
      <li>Found item report form</li>
      <li>Search results page</li>
    </ul>
    <p>HTML ensures that the system content is properly structured and accessible through web browsers.</p>

    <p><strong>CSS (Cascading Style Sheets)</strong><br>
    CSS is used to design and style the visual appearance of the web pages. It controls elements such as:</p>
    <ul>
      <li>Font styles and sizes</li>
      <li>Page layouts</li>
    </ul>
  </div>
</div>
"""

    # ---------------- PAGE 28: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 3) ----------------
    html += """
<!-- PAGE 28: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 3) -->
<div class="page">
  <div class="border-box">
    <ul>
      <li>Colors and backgrounds</li>
      <li>Spacing and alignment</li>
    </ul>
    <p>Using CSS improves the overall user experience by making the interface visually appealing and easy to navigate.</p>
    <p>Responsive design techniques are also implemented using CSS to ensure that the portal works properly on different screen sizes such as laptops, tablets, and smartphones.</p>

    <h2 class="sec-title">JavaScript and TypeScript</h2>
    <p>JavaScript and TypeScript are used to add interactivity and dynamic behavior to the web application.</p>
    <p>It allows the system to respond to user actions without reloading the entire page. Some uses of JavaScript in the UniFound portal include:</p>
    <ul>
      <li>Form validation before submission</li>
      <li>Interactive search functionality</li>
      <li>Dynamic display of item details</li>
      <li>Improved user interface responsiveness</li>
    </ul>
    <p>JavaScript enhances the usability of the platform by making it faster and more interactive.</p>

    <h2 class="sec-title">Database &ndash; PostgreSQL or SQLite</h2>
    <p>A database is required to store all system information such as user accounts and item reports.</p>
    <p>The UniFound system uses databases such as <strong>PostgreSQL or SQLite</strong> for storing and managing data with complete relational integrity.</p>

    <p><strong>PostgreSQL</strong><br>
    PostgreSQL is an advanced, enterprise-class open source relational database that stores data in structured tables with strict ACID compliance. It is suitable for applications that require high scalability, reliability, and robust data processing.</p>
    <p>Advantages of PostgreSQL include:</p>
    <ul>
      <li>High scalability and reliability</li>
      <li>Strong data consistency and transactions</li>
      <li>Advanced indexing and JSON document support</li>
      <li>Seamless cloud deployment integration</li>
    </ul>

    <p><strong>SQLite</strong><br>
    SQLite is a lightweight, serverless relational database engine used for development and local testing. It requires zero configuration while fully supporting standard SQL operations.</p>
  </div>
</div>
"""

    # ---------------- PAGE 29: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 4) ----------------
    html += """
<!-- PAGE 29: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 4) -->
<div class="page">
  <div class="border-box">
    <p>Advantages of SQLite include:</p>
    <ul>
      <li>Strong data consistency</li>
      <li>Structured data management</li>
      <li>High reliability</li>
      <li>Secure data storage</li>
    </ul>
    <p>The database stores information such as:</p>
    <ul>
      <li>User registration details</li>
      <li>Lost item reports</li>
      <li>Found item reports</li>
      <li>Item descriptions and images</li>
      <li>Claim requests</li>
    </ul>
    <p>This centralized data storage allows the UniFound system to retrieve and display information quickly.</p>

    <h2 class="sec-title">Development Tools</h2>
    <p>Several development tools are used to build and manage the UniFound project.</p>

    <p><strong>Visual Studio Code (VS Code)</strong><br>
    VS Code is a powerful source code editor used for writing and managing the project code. It supports multiple programming languages and provides useful features such as:</p>
    <ul>
      <li>Syntax highlighting</li>
      <li>Code auto-completion</li>
      <li>Debugging tools</li>
      <li>Extension support</li>
    </ul>
    <p>These features help developers write code efficiently and detect errors quickly.</p>

    <p><strong>GitHub</strong><br>
    GitHub is a platform used for version control and collaboration. It allows developers to store their project code in online repositories and track changes over time.</p>
    <p>Using GitHub provides several benefits:</p>
    <ul>
      <li>Backup of project files</li>
      <li>Version tracking</li>
      <li>Collaboration between team members</li>
      <li>Easy sharing of code</li>
    </ul>
    <p>GitHub ensures that the project remains organized and secure during development.</p>
  </div>
</div>
"""

    # ---------------- PAGE 30: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 5) ----------------
    html += """
<!-- PAGE 30: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 5) -->
<div class="page">
  <div class="border-box">
    <table class="report-table">
      <thead>
        <tr>
          <th style="width: 35%;">Software Component</th>
          <th style="width: 65%;">Specification / Description</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><strong>Operating System</strong></td><td>Windows 10 / Windows 11 / Linux</td></tr>
        <tr><td><strong>Programming Language</strong></td><td>Python 3.11+ / TypeScript</td></tr>
        <tr><td><strong>Frontend Technologies</strong></td><td>React 18, Vite, TypeScript, HTML, CSS</td></tr>
        <tr><td><strong>Backend Framework</strong></td><td>FastAPI (ASGI) / Python</td></tr>
        <tr><td><strong>Database</strong></td><td>PostgreSQL / SQLite with SQLAlchemy 2.0</td></tr>
        <tr><td><strong>Development Tools</strong></td><td>Visual Studio Code</td></tr>
        <tr><td><strong>Version Control</strong></td><td>Git and GitHub</td></tr>
        <tr><td><strong>Web Browser</strong></td><td>Google Chrome / Microsoft Edge / Mozilla Firefox</td></tr>
      </tbody>
    </table>
    <div class="table-caption">Table 4.1 &ndash; Software Requirements</div>

    <h2 class="sec-title" style="margin-top: 15px;">4.2 Hardware Requirements</h2>
    <p>Hardware requirements refer to the physical devices needed to develop, run, and access the UniFound portal.</p>
    <p>Since the system is a web-based platform, it does not require high-end hardware. However, a basic computer system is necessary for development and testing.</p>
    <p>The hardware requirements are described below.</p>

    <h2 class="sec-title">Processor</h2>
    <p>A processor such as <strong>Intel Core i3 or above</strong> is recommended for running the development environment and executing the application.</p>
    <p>The processor is responsible for performing computations, executing program instructions, and managing system operations.</p>
    <p>A faster processor improves system performance during tasks such as:</p>
    <ul>
      <li>Running the web server</li>
      <li>Processing database queries</li>
      <li>Handling user requests</li>
    </ul>
  </div>
</div>
"""

    # ---------------- PAGE 31: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 6) ----------------
    html += """
<!-- PAGE 31: CHAPTER 4 - SYSTEM REQUIREMENTS (PART 6) -->
<div class="page">
  <div class="border-box">
    <h2 class="sec-title">RAM</h2>
    <p>A minimum of <strong>4 GB RAM</strong> is required for smooth system performance.</p>
    <p>RAM (Random Access Memory) temporarily stores data and instructions that the processor needs during execution. Having sufficient RAM ensures that multiple applications such as the code editor, browser, and development server can run simultaneously without slowing down the system.</p>
    <p>Higher RAM capacity improves system responsiveness and development efficiency.</p>

    <h2 class="sec-title">Storage</h2>
    <p>A minimum of <strong>20 GB storage space</strong> is required to store the project files, development tools, database files, and related resources.</p>
    <p>Storage is also required for saving:</p>
    <ul>
      <li>Source code</li>
      <li>Database records</li>
      <li>Image files of lost or found items</li>
      <li>Software installations</li>
    </ul>
    <p>Adequate storage ensures that the system can store and manage data without interruptions.</p>

    <h2 class="sec-title">Internet Connection</h2>
    <p>An active <strong>internet connection</strong> is required for several purposes such as:</p>
    <ul>
      <li>Downloading development tools and libraries</li>
      <li>Accessing online documentation and resources</li>
      <li>Hosting the application on a server</li>
      <li>Allowing users to access the platform online</li>
    </ul>
    <p>The internet connection also enables users to report lost items and search for found items from different locations within the campus.</p>
    <p>In conclusion, the UniFound system requires only basic hardware and widely available software technologies, making it easy to develop, deploy, and maintain. These requirements ensure that the platform remains accessible to users while providing efficient performance for managing lost and found items within the university environment.</p>
  </div>
</div>
"""

    # ---------------- PAGE 32: CHAPTER 4 - HARDWARE TABLE ----------------
    html += """
<!-- PAGE 32: CHAPTER 4 - HARDWARE TABLE -->
<div class="page">
  <div class="border-box">
    <table class="report-table">
      <thead>
        <tr>
          <th style="width: 35%;">Hardware Component</th>
          <th style="width: 65%;">Minimum Requirement</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><strong>Processor</strong></td><td>Intel Core i3 or higher</td></tr>
        <tr><td><strong>RAM</strong></td><td>Minimum 4 GB</td></tr>
        <tr><td><strong>Storage</strong></td><td>Minimum 20 GB free space</td></tr>
        <tr><td><strong>Display</strong></td><td>1366 &times; 768 resolution</td></tr>
        <tr><td><strong>Internet</strong></td><td>Stable Internet Connection</td></tr>
        <tr><td><strong>Input Devices</strong></td><td>Keyboard and Mouse</td></tr>
      </tbody>
    </table>
    <div class="table-caption">Table 4.2 &ndash; Hardware Requirements</div>
  </div>
</div>
"""

    # ---------------- PAGE 33: CHAPTER 5 - EXPECTED OUTCOMES (PART 1) ----------------
    html += """
<!-- PAGE 33: CHAPTER 5 - EXPECTED OUTCOMES (PART 1) -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title">CHAPTER 5 &ndash; EXPECTED OUTCOMES</h1>
    <p>The expected outcome of the UniFound &ndash; Lost and Found Management Portal is to provide a digital platform that helps students and staff easily report, search, and recover lost items within the university campus. The system aims to replace the traditional manual process of managing lost items with a more efficient, organized, and user-friendly web application.</p>
    <p>By implementing this system, users will be able to quickly report lost or found items and search the database to find possible matches. The platform also improves transparency and communication between users and administrators.</p>
    <p>The graphical user interface (GUI) of the UniFound portal is designed to be simple, intuitive, and easy to use so that users with minimal technical knowledge can interact with the system efficiently.</p>
    <p>Below are the main expected outcomes and interfaces of the system.</p>

    <h2 class="sec-title">1. User Registration Page</h2>
    <p><strong>The user registration page allows new users to create an account on the UniFound portal. Students and staff members must register before accessing the system features.</strong></p>
    <p>The registration form collects basic information such as:</p>
    <ul>
      <li>Name</li>
      <li>Email address</li>
      <li>Password</li>
      <li>Contact information</li>
    </ul>
    <p>Once the user fills in the required details and submits the form, the system stores the information in the database and creates a new user account.</p>
    <p>The purpose of the registration system is to ensure that only authorized users can access the portal and report lost or found items.</p>
    <p>Expected outcome of this page:</p>
    <ul>
      <li>Secure user account creation</li>
      <li>Storage of user information in the database</li>
      <li>Controlled access to the system</li>
    </ul>

    <h2 class="sec-title">2. Login Page</h2>
    <p>The login page allows registered users to access their accounts by entering their credentials such as email and password.</p>
  </div>
</div>
"""

    # ---------------- PAGE 34: CHAPTER 5 - EXPECTED OUTCOMES (PART 2) ----------------
    html += """
<!-- PAGE 34: CHAPTER 5 - EXPECTED OUTCOMES (PART 2) -->
<div class="page">
  <div class="border-box">
    <p>After successful login, users are redirected to the main dashboard of the UniFound portal where they can access different features such as reporting lost items or searching for found items.</p>
    <p>The login system ensures that only authenticated users can use the platform.</p>
    <p>Expected outcome of this page:</p>
    <ul>
      <li>Secure user authentication</li>
      <li>Protection against unauthorized access</li>
      <li>Personalized user experience after login</li>
    </ul>

    <h2 class="sec-title">3. Report Lost Item Page</h2>
    <p>This page allows users to report items they have lost within the university campus.</p>
    <p>Users can submit detailed information about the lost item including:</p>
    <ul>
      <li>Item name</li>
      <li>Item description</li>
      <li>Category of the item</li>
      <li>Location where the item was lost</li>
      <li>Date of loss</li>
      <li>Optional image upload</li>
    </ul>
    <p>Once the form is submitted, the system stores the information in the database and makes it available for other users to search.</p>
    <p>Expected outcome of this page:</p>
    <ul>
      <li>Easy reporting of lost items</li>
      <li>Proper storage of item details in the system</li>
      <li>Increased chances of recovering lost belongings</li>
    </ul>

    <h2 class="sec-title">4. Report Found Item Page</h2>
    <p>This page allows users who find an item to report it on the portal.</p>
    <p>The form collects information similar to the lost item report, such as:</p>
    <ul>
      <li>Description of the found item</li>
      <li>Location where the item was found</li>
      <li>Category of the item</li>
    </ul>
  </div>
</div>
"""

    # ---------------- PAGE 35: CHAPTER 5 - EXPECTED OUTCOMES (PART 3) ----------------
    html += """
<!-- PAGE 35: CHAPTER 5 - EXPECTED OUTCOMES (PART 3) -->
<div class="page">
  <div class="border-box">
    <ul>
      <li>Optional image of the item</li>
    </ul>
    <p>Once submitted, the item details are stored in the database so that users who have lost similar items can search for them.</p>
    <p>Expected outcome of this page:</p>
    <ul>
      <li>Efficient reporting of found items</li>
      <li>Creation of a centralized lost and found database</li>
      <li>Faster item recovery process</li>
    </ul>

    <h2 class="sec-title">5. Search Item Page</h2>
    <p>The search page allows users to search for lost or found items in the system.</p>
    <p>Users can search using different filters such as:</p>
    <ul>
      <li>Item name</li>
      <li>Category</li>
      <li>Location</li>
      <li>Keywords</li>
    </ul>
    <p>The system retrieves relevant results from the database and displays them to the user.</p>
    <p>Expected outcome of this page:</p>
    <ul>
      <li>Quick and efficient item searching</li>
      <li>Easy identification of possible matches</li>
      <li>Improved chances of recovering lost items</li>
    </ul>

    <h2 class="sec-title">6. Claim Item Feature</h2>
    <p>If a user finds an item that matches their lost belongings, they can submit a claim request through the portal.</p>
    <p>The claim request is sent to the system administrator for verification. The administrator checks the details before approving the claim to ensure that the item is returned to the rightful owner.</p>
    <p>Expected outcome of this feature:</p>
    <ul>
      <li>Secure item recovery process</li>
      <li>Prevention of fraudulent claims</li>
      <li>Proper verification before item handover</li>
    </ul>
  </div>
</div>
"""

    # ---------------- PAGE 36: CHAPTER 5 - EXPECTED OUTCOMES (PART 4) ----------------
    html += """
<!-- PAGE 36: CHAPTER 5 - EXPECTED OUTCOMES (PART 4) -->
<div class="page">
  <div class="border-box">
    <h2 class="sec-title">7. Admin Dashboard</h2>
    <p>The admin dashboard is designed for system administrators who manage the entire platform.</p>
    <p>The administrator has several responsibilities including:</p>
    <ul>
      <li>Monitoring lost and found item reports</li>
      <li>Reviewing claim requests</li>
      <li>Approving or rejecting item claims</li>
      <li>Managing user accounts</li>
      <li>Removing incorrect or duplicate reports</li>
    </ul>
    <p>This ensures that the system remains organized and trustworthy.</p>
    <p>Expected outcome of this interface:</p>
    <ul>
      <li>Effective system management</li>
      <li>Monitoring of platform activities</li>
      <li>Ensuring fairness and security in item recovery</li>
    </ul>

    <h2 class="sec-title">Overall Expected Outcomes :</h2>
    <p><strong>The UniFound system is expected to deliver several benefits to the university community.</strong></p>
    <p><strong>Some key outcomes include:</strong></p>
    <ul>
      <li><strong>Faster reporting and recovery of lost items</strong></li>
      <li><strong>A centralized digital platform for managing lost and found records</strong></li>
      <li><strong>Improved communication between students and administrators</strong></li>
      <li><strong>Reduced dependence on manual record keeping</strong></li>
      <li><strong>Increased transparency and security in the lost item recovery process</strong></li>
    </ul>
    <p><strong>By implementing this system, universities can significantly improve the efficiency of lost and found management and help students recover their belongings more easily.</strong></p>
  </div>
</div>
"""

    # ---------------- PAGE 37: CHAPTER 5 - INTERFACE OVERVIEW ----------------
    html += """
<!-- PAGE 37: INTERFACE OVERVIEW -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title" style="font-size: 13pt; margin-bottom: 8px;">UniFound system interface overview :</h1>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 5px;">
      <!-- Card 1: Registration -->
      <div style="border: 1px solid #ccc; border-radius: 4px; padding: 6px; background: #fafafa; font-size: 8pt;">
        <div style="background: #2563eb; color: #fff; padding: 3px 6px; font-weight: bold; border-radius: 2px;">UniFound - Registration</div>
        <div style="margin: 4px 0; border: 1px solid #ddd; padding: 4px; background: #fff;">
          <strong>Name:</strong> [ Sahil Khot ]<br>
          <strong>Email:</strong> [ sahil@campus.edu ]<br>
          <strong>Password:</strong> [ •••••••• ]
        </div>
        <div style="text-align: center; font-weight: bold; font-size: 7.5pt; color: #555;">Fig 5.1 User Registration Interface</div>
      </div>

      <!-- Card 2: Login -->
      <div style="border: 1px solid #ccc; border-radius: 4px; padding: 6px; background: #fafafa; font-size: 8pt;">
        <div style="background: #2563eb; color: #fff; padding: 3px 6px; font-weight: bold; border-radius: 2px;">UniFound - Login</div>
        <div style="margin: 4px 0; border: 1px solid #ddd; padding: 4px; background: #fff;">
          <strong>Email:</strong> [ user@campus.edu ]<br>
          <strong>Password:</strong> [ •••••••• ]<br>
          <span style="background: #2563eb; color: #fff; padding: 1px 6px; font-size: 7pt; border-radius: 2px;">Sign In</span>
        </div>
        <div style="text-align: center; font-weight: bold; font-size: 7.5pt; color: #555;">Fig 5.2 User Login Interface</div>
      </div>

      <!-- Card 3: Report Lost -->
      <div style="border: 1px solid #ccc; border-radius: 4px; padding: 6px; background: #fafafa; font-size: 8pt;">
        <div style="background: #e11d48; color: #fff; padding: 3px 6px; font-weight: bold; border-radius: 2px;">Report Lost Item</div>
        <div style="margin: 4px 0; border: 1px solid #ddd; padding: 4px; background: #fff;">
          <strong>Item:</strong> [ Blue Dell Backpack ]<br>
          <strong>Category:</strong> [ Accessories ]<br>
          <strong>Location:</strong> [ Library 2nd Floor ]
        </div>
        <div style="text-align: center; font-weight: bold; font-size: 7.5pt; color: #555;">Fig 5.3 Lost Item Reporting Page</div>
      </div>

      <!-- Card 4: Report Found -->
      <div style="border: 1px solid #ccc; border-radius: 4px; padding: 6px; background: #fafafa; font-size: 8pt;">
        <div style="background: #16a34a; color: #fff; padding: 3px 6px; font-weight: bold; border-radius: 2px;">Report Found Item</div>
        <div style="margin: 4px 0; border: 1px solid #ddd; padding: 4px; background: #fff;">
          <strong>Item:</strong> [ Scientific Calculator ]<br>
          <strong>Found At:</strong> [ Lab 304 ]<br>
          <strong>Image:</strong> [ Uploaded &check; ]
        </div>
        <div style="text-align: center; font-weight: bold; font-size: 7.5pt; color: #555;">Fig 5.4 Found Item Reporting Page</div>
      </div>
    </div>

    <!-- Card 5: Admin Dashboard -->
    <div style="border: 1px solid #ccc; border-radius: 4px; padding: 8px; background: #fafafa; font-size: 8pt; margin-top: 10px;">
      <div style="background: #0f172a; color: #fff; padding: 4px 8px; font-weight: bold; border-radius: 2px; display: flex; justify-content: space-between;">
        <span>UniFound Admin Management Console</span>
        <span style="color: #4ade80;">Active</span>
      </div>
      <div style="display: flex; gap: 8px; margin: 6px 0;">
        <div style="flex: 1; background: #0284c7; color: #fff; padding: 6px; text-align: center; border-radius: 3px;"><strong>57</strong><br><small>Total Items</small></div>
        <div style="flex: 1; background: #16a34a; color: #fff; padding: 6px; text-align: center; border-radius: 3px;"><strong>25</strong><br><small>Recovered</small></div>
        <div style="flex: 1; background: #f59e0b; color: #fff; padding: 6px; text-align: center; border-radius: 3px;"><strong>12</strong><br><small>Pending Claims</small></div>
        <div style="flex: 1; background: #e11d48; color: #fff; padding: 6px; text-align: center; border-radius: 3px;"><strong>8</strong><br><small>Alerts</small></div>
      </div>
      <div style="text-align: center; font-weight: bold; font-size: 8pt; color: #555;">Fig 5.5 Item Search and Results Page</div>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 38: CHAPTER 6 - CONCLUSION & FUTURE SCOPE ----------------
    html += """
<!-- PAGE 38: CHAPTER 6 - CONCLUSION & FUTURE SCOPE -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title">CHAPTER 6 &ndash; CONCLUSION&amp;FUTURE SCOPE</h1>
    <h2 class="sec-title">6.1 Conclusion</h2>
    <p>The UniFound &ndash; Lost and Found Management Portal provides a modern and efficient solution for managing lost and found items within a university campus. In many educational institutions, lost items are traditionally handled through manual methods such as physical registers, notice boards, or direct communication with security staff. These methods are often time-consuming, unorganized, and inefficient.</p>
    <p>The UniFound system digitalizes the entire lost and found process by providing a centralized web platform where users can easily report lost items, submit information about found items, and search the system database to locate their belongings. By using modern web technologies, the platform improves accessibility and allows users to interact with the system from any device connected to the internet.</p>
    <p>The system also improves transparency and organization by storing all information in a structured database. Features such as user authentication, item reporting, search functionality, and claim verification help ensure that items are returned to their rightful owners securely.</p>
    <p>Overall, the UniFound portal reduces the difficulties associated with traditional lost and found systems and provides a more reliable, efficient, and user-friendly solution for managing lost items within university campuses.</p>

    <h2 class="sec-title">6.2 Future Work</h2>
    <p>Although the UniFound portal successfully provides a digital solution for lost and found item management, there are several opportunities for further improvements and enhancements in the future.</p>
    <p>One possible improvement is the development of a <strong>mobile application</strong> for the system. A dedicated mobile app would allow users to report lost or found items instantly through their smartphones, making the platform more accessible and convenient.</p>
    <p>Another future enhancement could involve the integration of <strong>AI-based image recognition technology</strong>. With this feature, users could upload images of lost items, and the system could automatically detect and match similar items reported in the database.</p>
    <p>The system could also be improved by implementing a <strong>push notification system</strong>. This feature would notify users in real time when a matching item is found or when their claim request has been approved.</p>
    <p>Additionally, the platform could be integrated with <strong>campus ID card systems</strong> to verify user identities automatically. This would further improve security and ensure that only authorized students or staff members can access the platform.</p>
    <p>With these future improvements, the UniFound system could become an even more powerful and intelligent platform for managing lost and found items within educational institutions.</p>
  </div>
</div>
"""

    # ---------------- PAGE 39: CHAPTER 7 - REFERENCES ----------------
    html += """
<!-- PAGE 39: CHAPTER 7 - REFERENCES -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title" style="margin-bottom: 18px;">CHAPTER 7 &ndash; REFERENCES</h1>
    <ol style="margin-left: 15px; padding-left: 10px; line-height: 1.5; font-size: 10pt;">
      <li style="margin-bottom: 8px;">Meiko Jensen, Jorg Schwenk, Nils Gruschka, Luigi Lo Iacono, &ldquo;On Technical Security Issues in Cloud Computing,&rdquo; Proceedings of IEEE International Conference on Cloud Computing (CLOUD-II), pp. 109&ndash;116, 2009.</li>
      <li style="margin-bottom: 8px;">Ian Sommerville, <em>Software Engineering</em>, 10th Edition, Pearson Education, 2016.</li>
      <li style="margin-bottom: 8px;">Roger S. Pressman and Bruce R. Maxim, <em>Software Engineering: A Practitioner's Approach</em>, 8th Edition, McGraw-Hill Education, 2015.</li>
      <li style="margin-bottom: 8px;">FastAPI Documentation, &ldquo;FastAPI Web Framework,&rdquo; Available at: <span style="color: #0284c7;">https://fastapi.tiangolo.com</span></li>
      <li style="margin-bottom: 8px;">React Documentation, &ldquo;React - The library for web and native user interfaces,&rdquo; Available at: <span style="color: #0284c7;">https://react.dev</span></li>
      <li style="margin-bottom: 8px;">W3Schools, &ldquo;JavaScript Tutorial,&rdquo; Available at: <span style="color: #0284c7;">https://www.w3schools.com/js/</span></li>
      <li style="margin-bottom: 8px;">Python Software Foundation, &ldquo;Python Documentation,&rdquo; Available at: <span style="color: #0284c7;">https://docs.python.org</span></li>
      <li style="margin-bottom: 8px;">SQLAlchemy Authors, &ldquo;SQLAlchemy 2.0 Documentation,&rdquo; Available at: <span style="color: #0284c7;">https://docs.sqlalchemy.org</span></li>
      <li style="margin-bottom: 8px;">PostgreSQL Global Development Group, &ldquo;PostgreSQL Documentation,&rdquo; Available at: <span style="color: #0284c7;">https://www.postgresql.org/docs/</span></li>
      <li style="margin-bottom: 8px;">Mozilla Developer Network (MDN), &ldquo;Web Development Guide,&rdquo; Available at: <span style="color: #0284c7;">https://developer.mozilla.org</span></li>
      <li style="margin-bottom: 8px;">Model Context Protocol Specification, &ldquo;MCP Protocol Documentation,&rdquo; Available at: <span style="color: #0284c7;">https://modelcontextprotocol.io</span></li>
      <li style="margin-bottom: 8px;">GitHub Documentation, &ldquo;Version Control and Collaboration,&rdquo; Available at: <span style="color: #0284c7;">https://docs.github.com</span></li>
    </ol>
  </div>
</div>
"""

    # ---------------- PAGE 40: CHAPTER 8 - WEEKLY REPORT ----------------
    html += """
<!-- PAGE 40: CHAPTER 8 - WEEKLY REPORT -->
<div class="page">
  <div class="border-box">
    <h1 class="chap-title">CHAPTER 8 &ndash; WEEKLY REPORT</h1>
    <p>The weekly report describes the progress and development activities performed during each week of the project. It shows how the project was planned, designed, implemented, and completed step by step.</p>

    <table class="report-table" style="font-size: 8pt; margin-top: 6px;">
      <thead>
        <tr>
          <th style="width: 14%;">Week No.</th>
          <th style="width: 86%;">Work Done / Progress Description</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Week 1</strong></td>
          <td>Project topic discussion with the guide and team members. Finalized the project title &ldquo;UniFound &ndash; Lost and Found Management Portal.&rdquo; Understood the problem of managing lost items in universities and defined the main objectives of the project.</td>
        </tr>
        <tr>
          <td><strong>Week 2</strong></td>
          <td>Performed background research and literature survey on existing lost and found systems. Studied similar platforms and identified their advantages and limitations. Prepared initial project planning and requirement analysis.</td>
        </tr>
        <tr>
          <td><strong>Week 3</strong></td>
          <td>Designed the overall system architecture and planned the project modules. Created system diagrams such as Use Case Diagram, ER Diagram, and Data Flow Diagram (DFD) to represent the system structure.</td>
        </tr>
        <tr>
          <td><strong>Week 4</strong></td>
          <td>Started frontend development of the UniFound portal. Designed basic pages such as Home Page, User Registration Page, and Login Page using React and modern CSS. Focused on creating a simple and user-friendly interface.</td>
        </tr>
        <tr>
          <td><strong>Week 5</strong></td>
          <td>Implemented backend functionality using Python and FastAPI. Developed modules for user authentication, registration, and login validation. Connected the frontend forms with backend logic.</td>
        </tr>
        <tr>
          <td><strong>Week 6</strong></td>
          <td>Developed the Lost Item Reporting Module where users can submit details about lost items including item name, description, category, and location. Stored the data in the database.</td>
        </tr>
        <tr>
          <td><strong>Week 7</strong></td>
          <td>Implemented the Found Item Reporting Module that allows users to report items they have found. Integrated the database to store item details and display them on the platform.</td>
        </tr>
        <tr>
          <td><strong>Week 8</strong></td>
          <td>Developed the Search and Claim Module that allows users to search for lost or found items and submit claim requests. Added filters for item categories and keywords.</td>
        </tr>
        <tr>
          <td><strong>Week 9</strong></td>
          <td>Implemented the Admin Dashboard to manage item reports, verify claim requests, and monitor system activities. Ensured that only authorized administrators can access this module.</td>
        </tr>
        <tr>
          <td><strong>Week 10</strong></td>
          <td>Performed system testing to identify and fix errors. Tested all modules such as login, item reporting, searching, and claim verification to ensure proper system functionality.</td>
        </tr>
        <tr>
          <td><strong>Week 11</strong></td>
          <td>Improved the user interface design and optimized the system performance. Made minor corrections in the system workflow and ensured smooth operation of the portal.</td>
        </tr>
        <tr>
          <td><strong>Week 12</strong></td>
          <td>Prepared the final project documentation and report including introduction, methodology, system design, results, and conclusion. Finalized the project for submission.</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    return html

def main():
    workspace = Path(r"C:\Users\MINAL PRASAD\OneDrive\Desktop\Unifound")
    html_file = workspace / "report.html"
    pdf_file = workspace / "UNIFOUND_PROJECT_REPORT.pdf"

    print("Generating HTML report...")
    content = generate_html_report()
    html_file.write_text(content, encoding="utf-8")
    print(f"Saved {html_file}")

    print("Converting HTML to PDF via Microsoft Edge headless...")
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_file}",
        f"file:///{html_file.as_posix()}"
    ]
    subprocess.run(cmd, check=True)
    
    if pdf_file.exists():
        size_kb = pdf_file.stat().st_size / 1024
        print(f"SUCCESS: Generated {pdf_file} ({size_kb:.2f} KB)")
    else:
        print("ERROR: PDF was not generated.")

if __name__ == "__main__":
    main()
