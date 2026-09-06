import os
import subprocess
import base64
import shutil
from pathlib import Path

def generate_user_manual_html() -> str:
    assets_dir = Path(__file__).parent / "extracted_assets"
    
    banner_b64 = ""
    crest_b64 = ""
    if (assets_dir / "page_1_X4.png").exists():
        with open(assets_dir / "page_1_X4.png", "rb") as f:
            banner_b64 = base64.b64encode(f.read()).decode("utf-8")
    if (assets_dir / "page_1_X15.png").exists():
        with open(assets_dir / "page_1_X15.png", "rb") as f:
            crest_b64 = base64.b64encode(f.read()).decode("utf-8")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>UNIFOUND - User Manual &amp; Operating Guide</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  body {{
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Arial, "Helvetica Neue", Helvetica, sans-serif;
    color: #1e293b;
    background: #fff;
    font-size: 10pt;
    line-height: 1.5;
  }}
  .page {{
    width: 210mm;
    height: 297mm;
    page-break-after: always;
    page-break-inside: avoid;
    padding: 12mm 14mm;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }}
  .border-box {{
    border: 1.5px solid #334155;
    height: 100%;
    width: 100%;
    padding: 24px 28px;
    display: flex;
    flex-direction: column;
    position: relative;
  }}
  .header-rule {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1.5px solid #0284c7;
    padding-bottom: 6px;
    margin-bottom: 14px;
    font-size: 8.5pt;
    color: #64748b;
    font-weight: 600;
  }}
  .footer-rule {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #cbd5e1;
    padding-top: 6px;
    margin-top: auto;
    font-size: 8pt;
    color: #64748b;
  }}
  h1.cover-title {{
    font-size: 20pt;
    font-weight: 800;
    color: #1e1b4b;
    text-align: center;
    margin: 10px 0 5px;
    letter-spacing: 0.5px;
  }}
  h2.cover-subtitle {{
    font-size: 12pt;
    font-weight: 700;
    color: #4338ca;
    text-align: center;
    margin: 0 0 15px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}
  h1.manual-title {{
    font-size: 15pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #6366f1;
    padding-bottom: 6px;
    margin: 0 0 14px 0;
    letter-spacing: 0.2px;
  }}
  h2.section-heading {{
    font-size: 12pt;
    font-weight: 700;
    color: #1e293b;
    margin: 14px 0 6px 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  h3.step-heading {{
    font-size: 10.5pt;
    font-weight: 700;
    color: #4338ca;
    margin: 10px 0 4px 0;
  }}
  p {{
    margin: 0 0 8px 0;
    text-align: justify;
    line-height: 1.45;
  }}
  .alert-card {{
    background: #f8fafc;
    border-left: 4px solid #6366f1;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 10px 0;
    font-size: 9.5pt;
  }}
  .alert-card.success {{
    border-left-color: #10b981;
    background: #f0fdf4;
  }}
  .alert-card.warning {{
    border-left-color: #f59e0b;
    background: #fffbeb;
  }}
  .step-box {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 12px;
  }}
  .step-num {{
    display: inline-block;
    background: #4f46e5;
    color: #fff;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    text-align: center;
    line-height: 22px;
    font-size: 9pt;
    font-weight: bold;
    margin-right: 6px;
  }}
  table.guide-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 9pt;
  }}
  table.guide-table th, table.guide-table td {{
    border: 1px solid #cbd5e1;
    padding: 7px 10px;
    text-align: left;
    vertical-align: top;
  }}
  table.guide-table th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
  }}
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 8pt;
    font-weight: 700;
    text-transform: uppercase;
  }}
  .badge-lost {{ background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }}
  .badge-found {{ background: #dcfce7; color: #15803d; border: 1px solid #86efac; }}
  .badge-pending {{ background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }}
  .badge-approved {{ background: #e0e7ff; color: #4338ca; border: 1px solid #a5b4fc; }}
  .code-inline {{
    background: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
    font-family: Consolas, monospace;
    font-size: 8.5pt;
  }}
  .flow-diagram {{
    display: flex;
    justify-content: space-around;
    align-items: center;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    margin: 12px 0;
  }}
  .flow-node {{
    background: #fff;
    border: 1.5px solid #6366f1;
    border-radius: 6px;
    padding: 8px 12px;
    text-align: center;
    font-size: 8.5pt;
    font-weight: bold;
    color: #1e1b4b;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  .flow-arrow {{
    font-size: 14pt;
    color: #6366f1;
    font-weight: bold;
  }}
</style>
</head>
<body>
"""

    # ---------------- PAGE 1: COVER ----------------
    html += f"""
<!-- PAGE 1: COVER -->
<div class="page">
  <div class="border-box" style="align-items: center; justify-content: space-between; text-align: center;">
    <div style="width: 100%; text-align: left; margin-bottom: 5px;">
      <img src="data:image/png;base64,{banner_b64}" style="height: 48px; width: auto; object-fit: contain;" alt="Parul University NAAC A++">
    </div>

    <div>
      <h1 class="cover-title">UNIFOUND MANAGEMENT SYSTEM</h1>
      <h2 class="cover-subtitle">Complete Application User Manual &amp; Operating Guide</h2>
      <div style="font-size: 10.5pt; color: #64748b; font-weight: 600;">A Step-by-Step Practical Guide for Students, Faculty &amp; Campus Administrators</div>
    </div>

    <!-- Official University Crest Logo -->
    <div style="margin: 10px 0;">
      <img src="data:image/png;base64,{crest_b64}" style="height: 145px; width: auto; object-fit: contain;" alt="Parul University Crest">
    </div>

    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 20px; width: 90%; text-align: left; margin: 10px 0;">
      <div style="font-size: 10.5pt; font-weight: bold; color: #1e1b4b; margin-bottom: 8px; text-align: center;">🚀 SYSTEM ACCESS QUICK REFERENCE</div>
      <table style="width: 100%; font-size: 9pt; border-collapse: collapse;">
        <tr>
          <td style="padding: 4px; font-weight: bold; width: 35%;">🌐 Web Application:</td>
          <td style="padding: 4px;"><a href="https://unifound-app.vercel.app" style="color: #4f46e5; text-decoration: none; font-weight: bold;">https://unifound-app.vercel.app</a></td>
        </tr>
        <tr>
          <td style="padding: 4px; font-weight: bold;">⚡ Backend API &amp; Swagger:</td>
          <td style="padding: 4px;"><a href="https://unifound-mqga.onrender.com" style="color: #4f46e5; text-decoration: none;">https://unifound-mqga.onrender.com</a></td>
        </tr>
        <tr>
          <td style="padding: 4px; font-weight: bold;">🔐 Default Admin ID:</td>
          <td style="padding: 4px; font-family: monospace; font-weight: bold; color: #b91c1c;">admin@campus.edu</td>
        </tr>
        <tr>
          <td style="padding: 4px; font-weight: bold;">🔑 Default Password:</td>
          <td style="padding: 4px; font-family: monospace; font-weight: bold; color: #b91c1c;">AdminPass123!</td>
        </tr>
      </table>
    </div>

    <div style="font-size: 9.5pt; line-height: 1.45;">
      <strong>Project Team Members:</strong><br>
      Sahil Khot (2303051240190) &bull; Shivani Choudhary (2303051240212)<br>
      Minal Prasad (2303051240122) &bull; Shivang Bhadwal (2303051240211)<br>
      <strong>Project Guide:</strong> Mrs. Arpita Meet Vaidya
    </div>

    <div style="font-size: 9.5pt; line-height: 1.35; margin-top: 5px;">
      <strong style="color: #b91c1c;">DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING</strong><br>
      <strong>PARUL INSTITUTE OF TECHNOLOGY, VADODARA, GUJARAT &bull; 2025&ndash;2026</strong>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 2: TABLE OF CONTENTS & GETTING STARTED ----------------
    html += """
<!-- PAGE 2: TABLE OF CONTENTS & GETTING STARTED -->
<div class="page">
  <div class="border-box">
    <div class="header-rule">
      <span>UNIFOUND OPERATING MANUAL</span>
      <span>TABLE OF CONTENTS &amp; GETTING STARTED</span>
    </div>

    <h1 class="manual-title">Table of Contents &amp; Quick Overview</h1>

    <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 18px; font-size: 9.5pt;">
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dotted #cbd5e1; padding-bottom: 3px;">
        <span><strong>1. Introduction to UniFound System</strong> &ndash; Purpose, Core Features, Architecture</span>
        <strong>Page 3</strong>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dotted #cbd5e1; padding-bottom: 3px;">
        <span><strong>2. Account Registration &amp; Authentication</strong> &ndash; Sign Up, Login, Profile Management</span>
        <strong>Page 4</strong>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dotted #cbd5e1; padding-bottom: 3px;">
        <span><strong>3. Reporting Lost &amp; Found Items</strong> &ndash; Categories, Locations, Photo Uploads</span>
        <strong>Page 5</strong>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dotted #cbd5e1; padding-bottom: 3px;">
        <span><strong>4. Browsing, Searching &amp; AI Matching</strong> &ndash; Filters, AI Confidence Engine</span>
        <strong>Page 6</strong>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dotted #cbd5e1; padding-bottom: 3px;">
        <span><strong>5. Submitting &amp; Managing Claims</strong> &ndash; Proof of Ownership, Claim Lifecycle</span>
        <strong>Page 7</strong>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dotted #cbd5e1; padding-bottom: 3px;">
        <span><strong>6. Administrator Portal &amp; Moderation</strong> &ndash; Claim Approval, Item Status, Audit Logs</span>
        <strong>Page 8</strong>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dotted #cbd5e1; padding-bottom: 3px;">
        <span><strong>7. Advanced Capabilities (MCP Agent &amp; Vision)</strong> &ndash; Automated Discovery &amp; AI Chat</span>
        <strong>Page 9</strong>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dotted #cbd5e1; padding-bottom: 3px;">
        <span><strong>8. Troubleshooting &amp; Frequently Asked Questions (FAQ)</strong> &ndash; Security &amp; Help Desk</span>
        <strong>Page 10</strong>
      </div>
    </div>

    <h2 class="section-heading">🎯 System Architecture &amp; User Roles</h2>
    <p>UniFound operates with two distinct privilege tiers to guarantee secure handover and fraud prevention:</p>

    <div style="display: flex; gap: 14px; margin-top: 8px;">
      <div style="flex: 1; background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 12px;">
        <div style="font-weight: bold; color: #166534; font-size: 10pt; margin-bottom: 4px;">🎓 Campus User (Student / Faculty)</div>
        <ul style="margin: 0; padding-left: 18px; font-size: 9pt; line-height: 1.4;">
          <li>Report misplaced or recovered articles with images</li>
          <li>Search active listings via keywords &amp; categories</li>
          <li>Receive automated AI match notifications</li>
          <li>File claim requests with private proof of ownership</li>
          <li>Track real-time status of claims and personal reports</li>
        </ul>
      </div>

      <div style="flex: 1; background: #eff6ff; border: 1px solid #93c5fd; border-radius: 8px; padding: 12px;">
        <div style="font-weight: bold; color: #1e40af; font-size: 10pt; margin-bottom: 4px;">🛡️ Campus Administrator (Security Office)</div>
        <ul style="margin: 0; padding-left: 18px; font-size: 9pt; line-height: 1.4;">
          <li>Review pending ownership claims and submitted proofs</li>
          <li>Approve or reject claims with official comments</li>
          <li>Manage item lifecycle (Open &rarr; Claim Pending &rarr; Claimed)</li>
          <li>Oversee campus security custody of high-value items</li>
          <li>Access comprehensive audit trail for institutional accountability</li>
        </ul>
      </div>
    </div>

    <div class="alert-card success" style="margin-top: 14px;">
      <strong>💡 Cloud Deployment Status:</strong> The application is fully live and cloud-hosted. Front-end assets are served globally via <strong>Vercel CDN</strong> (<a href="https://unifound-app.vercel.app">https://unifound-app.vercel.app</a>), while backend REST endpoints execute on <strong>Render Cloud</strong> (<a href="https://unifound-mqga.onrender.com">https://unifound-mqga.onrender.com</a>) backed by PostgreSQL database and JWT token security.
    </div>

    <div class="footer-rule">
      <span>Parul University &bull; Faculty of IT &amp; Computer Science</span>
      <span>Page 2 of 10</span>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 3: INTRODUCTION & WORKFLOW ----------------
    html += """
<!-- PAGE 3: INTRODUCTION & WORKFLOW -->
<div class="page">
  <div class="border-box">
    <div class="header-rule">
      <span>UNIFOUND OPERATING MANUAL</span>
      <span>CHAPTER 1: SYSTEM WORKFLOW</span>
    </div>

    <h1 class="manual-title">1. Introduction &amp; Core Operating Workflow</h1>

    <p><strong>UniFound</strong> is an enterprise-grade campus Lost &amp; Found management portal developed specifically for university environments. Traditional campus paper registers and unorganized bulletin boards suffer from high recovery latency, loss of claimant privacy, and vulnerability to fraudulent claims. UniFound solves these challenges through structured digital reporting, automated multi-factor AI matching, and centralized administrative verification.</p>

    <h2 class="section-heading">🔄 The Complete End-to-End Recovery Lifecycle</h2>
    <p>The diagram below illustrates the operational pathway taken from the moment an item is misplaced or found on campus until it is safely reunited with its rightful owner:</p>

    <div class="flow-diagram">
      <div class="flow-node">1. Item Reported<br><small>(Lost or Found)</small></div>
      <div class="flow-arrow">&rarr;</div>
      <div class="flow-node">2. AI Matching<br><small>(Scoring Engine)</small></div>
      <div class="flow-arrow">&rarr;</div>
      <div class="flow-node">3. Notification<br><small>(Alert Sent)</small></div>
      <div class="flow-arrow">&rarr;</div>
      <div class="flow-node">4. Claim Filed<br><small>(Proof Uploaded)</small></div>
      <div class="flow-arrow">&rarr;</div>
      <div class="flow-node">5. Admin Review<br><small>(Approve/Reject)</small></div>
      <div class="flow-arrow">&rarr;</div>
      <div class="flow-node">6. Handover<br><small>(Resolved)</small></div>
    </div>

    <h2 class="section-heading">✨ Core Technological Highlights</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px;">
      <div class="step-box">
        <strong style="color: #4338ca;">⚡ AI Multi-Factor Matching</strong>
        <p style="font-size: 8.5pt; margin-top: 4px;">Whenever an item is submitted, the system automatically runs a weighted matching algorithm evaluating: Category match (35%), Text &amp; keyword similarity (30%), Date proximity (20%), and Visual color/metadata (15%). If the confidence score exceeds 60%, instant alerts are created.</p>
      </div>
      <div class="step-box">
        <strong style="color: #4338ca;">🔒 Secure Verification &amp; Privacy</strong>
        <p style="font-size: 8.5pt; margin-top: 4px;">Identifying marks, serial numbers, and private item attributes are never published publicly. Only administrators can review claimant proofs, preventing unauthorized individuals from falsely claiming valuables.</p>
      </div>
      <div class="step-box">
        <strong style="color: #4338ca;">🖼️ Automated Image Analysis</strong>
        <p style="font-size: 8.5pt; margin-top: 4px;">Integrated Pillow (PIL) computer vision extracts dominant color profiles, aspect ratios, and format attributes to enrich item listings and assist automated visual comparisons.</p>
      </div>
      <div class="step-box">
        <strong style="color: #4338ca;">🤖 Model Context Protocol (MCP)</strong>
        <p style="font-size: 8.5pt; margin-top: 4px;">UniFound includes an integrated MCP tool server that enables LLM agents to autonomously query lost/found records, perform natural language diagnostics, and assist users conversationally.</p>
      </div>
    </div>

    <div class="alert-card">
      <strong>📌 Accessing the System:</strong> Open any modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari on iOS/Android) and navigate to <strong><a href="https://unifound-app.vercel.app">https://unifound-app.vercel.app</a></strong>.
    </div>

    <div class="footer-rule">
      <span>Parul University &bull; Faculty of IT &amp; Computer Science</span>
      <span>Page 3 of 10</span>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 4: REGISTRATION & AUTHENTICATION ----------------
    html += """
<!-- PAGE 4: REGISTRATION & AUTHENTICATION -->
<div class="page">
  <div class="border-box">
    <div class="header-rule">
      <span>UNIFOUND OPERATING MANUAL</span>
      <span>CHAPTER 2: ACCOUNT MANAGEMENT</span>
    </div>

    <h1 class="manual-title">2. Account Registration, Login &amp; Profiles</h1>

    <p>To ensure security and maintain a verifiable chain of custody, reporting items and filing claims requires an authenticated account.</p>

    <h2 class="section-heading">📝 Step 1: Registering a New Student / Faculty Account</h2>
    <div class="step-box">
      <span class="step-num">1</span> <strong>Navigate to the Registration Page:</strong> Click <strong>"Register"</strong> on the top navigation bar or browse to <span class="code-inline">https://unifound-app.vercel.app/register</span>.<br>
      <span class="step-num">2</span> <strong>Fill in Required Information:</strong>
      <ul style="margin: 4px 0 6px 20px; font-size: 9pt;">
        <li><strong>Full Name:</strong> Enter your official university name (e.g., <em>Minal Prasad</em>).</li>
        <li><strong>Email Address:</strong> Provide your active university or personal email (e.g., <em>minal@paruluniversity.ac.in</em>).</li>
        <li><strong>Password:</strong> Choose a strong password (minimum 8 characters with letters, numbers, and symbols).</li>
        <li><strong>Phone Number (Optional):</strong> Mobile number for SMS/call verification.</li>
        <li><strong>Department:</strong> Department name (e.g., <em>Computer Science &amp; Engineering</em>).</li>
        <li><strong>Student / Staff ID:</strong> University Enrollment Number (e.g., <em>2303051240122</em>).</li>
      </ul>
      <span class="step-num">3</span> <strong>Submit:</strong> Click <strong>"Create Account"</strong>. Your account is immediately activated with the standard <span class="badge badge-approved">USER</span> role.
    </div>

    <h2 class="section-heading">🔑 Step 2: Logging In</h2>
    <div class="step-box">
      <span class="step-num">1</span> Go to the Login Page at <span class="code-inline">/login</span>.<br>
      <span class="step-num">2</span> Enter your registered <strong>Email Address</strong> and <strong>Password</strong>.<br>
      <span class="step-num">3</span> Click <strong>"Sign In"</strong>. Upon successful authentication, the server generates an encrypted JSON Web Token (JWT) with 24-hour validity stored securely in client storage.
    </div>

    <h2 class="section-heading">👤 Managing Your Profile</h2>
    <p>Click on your avatar or username at the top right corner and select <strong>"Profile"</strong> (<span class="code-inline">/profile</span>) to:</p>
    <ul>
      <li>Update contact numbers and department details.</li>
      <li>Review your personal activity statistics (Total items reported, Active claims, Resolved recoveries).</li>
      <li>View your recent match alerts and security status.</li>
    </ul>

    <div class="alert-card warning">
      <strong>⚠️ Password Security Best Practice:</strong> Never share your login credentials with others. If you suspect your account has been compromised, contact the security department immediately.
    </div>

    <div class="footer-rule">
      <span>Parul University &bull; Faculty of IT &amp; Computer Science</span>
      <span>Page 4 of 10</span>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 5: REPORTING ITEMS ----------------
    html += """
<!-- PAGE 5: REPORTING ITEMS -->
<div class="page">
  <div class="border-box">
    <div class="header-rule">
      <span>UNIFOUND OPERATING MANUAL</span>
      <span>CHAPTER 3: REPORTING ITEMS</span>
    </div>

    <h1 class="manual-title">3. How to Report Lost &amp; Found Items</h1>

    <p>Whether you have misplaced personal property or found an unattended article on campus, reporting it promptly maximizes the recovery rate.</p>

    <div style="display: flex; gap: 12px; margin-bottom: 12px;">
      <div style="flex: 1; background: #fff1f2; border: 1.5px solid #fecdd3; border-radius: 8px; padding: 12px;">
        <div style="font-weight: bold; color: #be123c; font-size: 10pt;">📦 Reporting a LOST Item</div>
        <p style="font-size: 8.5pt; margin: 4px 0 6px;">Use when you have lost an item on campus.</p>
        <span class="code-inline">URL: /report-lost</span>
      </div>
      <div style="flex: 1; background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 8px; padding: 12px;">
        <div style="font-weight: bold; color: #15803d; font-size: 10pt;">🎁 Reporting a FOUND Item</div>
        <p style="font-size: 8.5pt; margin: 4px 0 6px;">Use when you have discovered an unattended item.</p>
        <span class="code-inline">URL: /report-found</span>
      </div>
    </div>

    <h2 class="section-heading">📋 Field-by-Field Submission Guide</h2>
    <table class="guide-table">
      <tr>
        <th style="width: 25%;">Field Name</th>
        <th style="width: 25%;">Type / Requirement</th>
        <th style="width: 50%;">Guidance &amp; Best Practices</th>
      </tr>
      <tr>
        <td><strong>Item Title</strong></td>
        <td>Text (Required)</td>
        <td>Be clear and specific (e.g., <em>"Black Dell G15 Laptop Charger"</em> instead of just <em>"Charger"</em>).</td>
      </tr>
      <tr>
        <td><strong>Item Type</strong></td>
        <td>Selection (Required)</td>
        <td>Select <span class="badge badge-lost">LOST</span> or <span class="badge badge-found">FOUND</span>.</td>
      </tr>
      <tr>
        <td><strong>Category</strong></td>
        <td>Dropdown (Required)</td>
        <td>Choose from: <em>Electronics, Identity &amp; Documents, Keys, Wallets &amp; Bags, Clothing, Books, Other</em>.</td>
      </tr>
      <tr>
        <td><strong>Campus Location</strong></td>
        <td>Text / Select (Required)</td>
        <td>Specify exact building &amp; room (e.g., <em>"Central Library 2nd Floor, Reading Room B"</em>).</td>
      </tr>
      <tr>
        <td><strong>Date &amp; Time</strong></td>
        <td>Date Picker (Required)</td>
        <td>Estimated date and time when the item was lost or discovered.</td>
      </tr>
      <tr>
        <td><strong>Description</strong></td>
        <td>Textarea (Required)</td>
        <td>Provide physical traits: color, brand, stickers, scratches, wear marks, case type.</td>
      </tr>
      <tr>
        <td><strong>Photograph</strong></td>
        <td>Image Upload (Recommended)</td>
        <td>Upload a clear JPG/PNG photo. Helps the AI matching engine and visual verification.</td>
      </tr>
      <tr>
        <td><strong>Custody / Handover</strong></td>
        <td>Text (Found items only)</td>
        <td>Where the item is currently kept (e.g., <em>"Handed over to PIT Security Desk Main Gate"</em>).</td>
      </tr>
    </table>

    <div class="alert-card warning">
      <strong>⚠️ Critical Privacy Rule for High-Value Items:</strong> For items containing sensitive data or high monetary value (such as wallets with cash or laptops with passwords), do <strong>NOT</strong> post exact PINs, passwords, or total cash amounts in the public description. Keep those details as private proof for the claim verification stage!
    </div>

    <div class="footer-rule">
      <span>Parul University &bull; Faculty of IT &amp; Computer Science</span>
      <span>Page 5 of 10</span>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 6: SEARCH & AI MATCHING ----------------
    html += """
<!-- PAGE 6: SEARCH & AI MATCHING -->
<div class="page">
  <div class="border-box">
    <div class="header-rule">
      <span>UNIFOUND OPERATING MANUAL</span>
      <span>CHAPTER 4: SEARCH &amp; AI MATCHING</span>
    </div>

    <h1 class="manual-title">4. Search System &amp; Automated AI Matching</h1>

    <h2 class="section-heading">🔍 How to Search Campus Items</h2>
    <p>The Search Portal (<span class="code-inline">https://unifound-app.vercel.app/search</span>) provides instant query filtering across all publicly active lost and found listings:</p>

    <div class="step-box">
      <ul style="margin: 0; padding-left: 18px; font-size: 9pt; line-height: 1.5;">
        <li><strong>Keyword Search:</strong> Type keywords such as brand names (<em>"Apple", "Sony", "Titan"</em>), colors, or descriptions.</li>
        <li><strong>Category Filter:</strong> Filter exclusively by Electronics, Keys, Wallets, Documents, etc.</li>
        <li><strong>Status Toggle:</strong> Switch between <em>Active/Open</em> items and <em>Resolved</em> items.</li>
        <li><strong>Location Filter:</strong> Narrow down to specific campuses, buildings, or cafeterias.</li>
      </ul>
    </div>

    <h2 class="section-heading">🤖 The Automated AI Matching Engine</h2>
    <p>UniFound features a background intelligence pipeline that continuously evaluates newly reported items against existing database records to detect potential matches automatically.</p>

    <table class="guide-table">
      <tr>
        <th>Matching Factor</th>
        <th>Weight</th>
        <th>How It Works</th>
      </tr>
      <tr>
        <td><strong>Category Match</strong></td>
        <td><strong>35%</strong></td>
        <td>Ensures matching items belong to the same functional taxonomy (e.g., Electronics to Electronics).</td>
      </tr>
      <tr>
        <td><strong>Text Similarity</strong></td>
        <td><strong>30%</strong></td>
        <td>Analyzes title keywords, token intersections, and description phrases using fuzzy text scoring.</td>
      </tr>
      <tr>
        <td><strong>Date Proximity</strong></td>
        <td><strong>20%</strong></td>
        <td>Calculates temporal difference between loss date and discovery date (highest score if within 48h).</td>
      </tr>
      <tr>
        <td><strong>Visual / Location</strong></td>
        <td><strong>15%</strong></td>
        <td>Compares campus zone proximity and automated Pillow visual characteristics (dominant color profiles).</td>
      </tr>
    </table>

    <h3 class="step-heading">Understanding Confidence Score Badges</h3>
    <div style="display: flex; gap: 10px; margin: 10px 0;">
      <div style="flex: 1; background: #ecfdf5; border: 1px solid #10b981; border-radius: 6px; padding: 8px; text-align: center;">
        <span style="font-weight: bold; color: #047857; font-size: 9pt;">🟢 High Match (80% &ndash; 100%)</span><br>
        <small>Strong match on category, title, date, and location.</small>
      </div>
      <div style="flex: 1; background: #fffbeb; border: 1px solid #f59e0b; border-radius: 6px; padding: 8px; text-align: center;">
        <span style="font-weight: bold; color: #b45309; font-size: 9pt;">🟡 Moderate Match (60% &ndash; 79%)</span><br>
        <small>Partial overlap in description or neighboring date.</small>
      </div>
      <div style="flex: 1; background: #f8fafc; border: 1px solid #94a3b8; border-radius: 6px; padding: 8px; text-align: center;">
        <span style="font-weight: bold; color: #475569; font-size: 9pt;">⚪ Low Match (&lt; 60%)</span><br>
        <small>Weak correlation; manual review advised.</small>
      </div>
    </div>

    <div class="alert-card success">
      <strong>🔔 Instant Match Notifications:</strong> When a match score exceeds 60%, UniFound automatically generates an alert in your notification center (<span class="code-inline">/notifications</span>) with a direct link to the matched item so you can immediately submit an ownership claim!
    </div>

    <div class="footer-rule">
      <span>Parul University &bull; Faculty of IT &amp; Computer Science</span>
      <span>Page 6 of 10</span>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 7: SUBMITTING CLAIMS ----------------
    html += """
<!-- PAGE 7: SUBMITTING CLAIMS -->
<div class="page">
  <div class="border-box">
    <div class="header-rule">
      <span>UNIFOUND OPERATING MANUAL</span>
      <span>CHAPTER 5: CLAIM VERIFICATION</span>
    </div>

    <h1 class="manual-title">5. How to File an Ownership Claim</h1>

    <p>When you discover an item in the public catalog that belongs to you, you must submit a formal <strong>Claim Request</strong> to establish genuine ownership before physical handover can take place.</p>

    <h2 class="section-heading">📝 Step-by-Step Claim Submission Flow</h2>
    <div class="step-box">
      <span class="step-num">1</span> <strong>Open Item Details:</strong> Click on the item card from the search results or notification alert to view its details page (<span class="code-inline">/items/:id</span>).<br>
      <span class="step-num">2</span> <strong>Click "Claim This Item":</strong> If the item is marked <span class="badge badge-found">FOUND</span> and its status is <span class="badge badge-lost">OPEN</span>, the <strong>"Claim Item"</strong> button will be active.<br>
      <span class="step-num">3</span> <strong>Fill the Claim Form:</strong>
      <ul style="margin: 4px 0 6px 20px; font-size: 9pt;">
        <li><strong>Detailed Proof of Ownership:</strong> State unmentioned identifying details (e.g., lock-screen wallpaper, unique scratch under the charging port, engraved initials, serial number, contents of internal pouch).</li>
        <li><strong>Supporting Proof / File Attachment:</strong> Upload purchase invoices, photos of you using the item previously, or an ID card copy.</li>
        <li><strong>Contact Number:</strong> A phone number where the security office can reach you for handover.</li>
      </ul>
      <span class="step-num">4</span> <strong>Submit Claim:</strong> Confirm the declaration and click <strong>"Submit Claim"</strong>.
    </div>

    <h2 class="section-heading">📊 The Claim Status Lifecycle</h2>
    <p>Track the progress of your submitted claims at <span class="code-inline">/my-claims</span>:</p>

    <div style="display: flex; flex-direction: column; gap: 8px; margin: 10px 0;">
      <div style="background: #fffbeb; border: 1px solid #fef3c7; border-left: 4px solid #f59e0b; padding: 8px 12px; border-radius: 4px; font-size: 9pt;">
        <span class="badge badge-pending">PENDING</span> &ndash; Your claim has been received and queued for administrative review by campus security.
      </div>
      <div style="background: #ecfdf5; border: 1px solid #d1fae5; border-left: 4px solid #10b981; padding: 8px 12px; border-radius: 4px; font-size: 9pt;">
        <span class="badge badge-approved">APPROVED</span> &ndash; Your proof has been authenticated! You may proceed to the designated security desk with your university ID card to collect the item.
      </div>
      <div style="background: #fef2f2; border: 1px solid #fee2e2; border-left: 4px solid #ef4444; padding: 8px 12px; border-radius: 4px; font-size: 9pt;">
        <span class="badge badge-lost">REJECTED</span> &ndash; The provided proof did not match the physical characteristics. Admin notes will indicate the reason.
      </div>
    </div>

    <div class="alert-card warning">
      <strong>⚖️ Anti-Fraud Institutional Policy:</strong> Submitting fraudulent claims for articles belonging to others is a violation of the Parul University Student Code of Conduct and will result in disciplinary action and account deactivation.
    </div>

    <div class="footer-rule">
      <span>Parul University &bull; Faculty of IT &amp; Computer Science</span>
      <span>Page 7 of 10</span>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 8: ADMINISTRATOR PORTAL ----------------
    html += """
<!-- PAGE 8: ADMINISTRATOR PORTAL -->
<div class="page">
  <div class="border-box">
    <div class="header-rule">
      <span>UNIFOUND OPERATING MANUAL</span>
      <span>CHAPTER 6: ADMINISTRATOR MANUAL</span>
    </div>

    <h1 class="manual-title">6. Campus Administrator Portal &amp; Moderation</h1>

    <p>The Administrator Portal is reserved for authorized campus security personnel and department coordinators to moderate reports, verify claims, and maintain campus-wide chain of custody.</p>

    <h2 class="section-heading">🔑 Logging In as Administrator</h2>
    <div class="step-box">
      <strong>Login URL:</strong> <span class="code-inline">https://unifound-app.vercel.app/login</span><br>
      <strong>Default Admin ID:</strong> <span class="code-inline" style="color: #b91c1c; font-weight: bold;">admin@campus.edu</span><br>
      <strong>Default Password:</strong> <span class="code-inline" style="color: #b91c1c; font-weight: bold;">AdminPass123!</span>
    </div>

    <h2 class="section-heading">🛡️ Admin Dashboard Features (/admin)</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 6px;">
      <div class="step-box">
        <strong style="color: #1e40af;">📊 Real-time Metric Cards</strong>
        <p style="font-size: 8.5pt; margin-top: 4px;">Instantly monitor Total Items Reported, Active Lost Listings, Recovered Found Items, Pending Verification Claims, and Resolution Rates.</p>
      </div>
      <div class="step-box">
        <strong style="color: #1e40af;">🔍 Item Catalog Moderation</strong>
        <p style="font-size: 8.5pt; margin-top: 4px;">Filter items across all categories, edit custody locations, archive stale entries, or mark items as Claimed / Resolved.</p>
      </div>
    </div>

    <h2 class="section-heading">⚖️ Processing Claim Requests (/admin/claims)</h2>
    <p>The Claim Moderation Queue displays all claims filed by campus users:</p>
    <div class="step-box">
      <span class="step-num">1</span> <strong>Review Claimant Information:</strong> Inspect claimant's full name, student ID, department, and telephone number.<br>
      <span class="step-num">2</span> <strong>Inspect Submitted Ownership Proof:</strong> Compare the claimant's private statement against the physical item in custody.<br>
      <span class="step-num">3</span> <strong>Take Moderation Action:</strong>
      <ul style="margin: 4px 0 0 20px; font-size: 9pt;">
        <li><strong style="color: #16a34a;">Approve Claim:</strong> Marks the claim as <span class="badge badge-approved">APPROVED</span> and transitions the item to <span class="badge badge-found">CLAIMED</span>. An automated notification instructs the student to collect the item.</li>
        <li><strong style="color: #dc2626;">Reject Claim:</strong> Provide an administrative comment explaining why the proof was insufficient (e.g., <em>"Serial number mismatch"</em>).</li>
      </ul>
    </div>

    <div class="alert-card success">
      <strong>📑 Security Audit Trail:</strong> Every administrative action (claim approval, rejection, item status modification) is logged with timestamp, administrator ID, and action description in the immutable <span class="code-inline">audit_logs</span> database table for institutional auditability.
    </div>

    <div class="footer-rule">
      <span>Parul University &bull; Faculty of IT &amp; Computer Science</span>
      <span>Page 8 of 10</span>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 9: ADVANCED MCP AGENT ----------------
    html += """
<!-- PAGE 9: ADVANCED MCP AGENT -->
<div class="page">
  <div class="border-box">
    <div class="header-rule">
      <span>UNIFOUND OPERATING MANUAL</span>
      <span>CHAPTER 7: ADVANCED MCP AGENT</span>
    </div>

    <h1 class="manual-title">7. AI Agent &amp; Model Context Protocol (MCP)</h1>

    <p>UniFound integrates the open <strong>Model Context Protocol (MCP)</strong> standard, exposing tools that enable autonomous AI agents (such as Google Gemini, Claude, or local ReAct agents) to interact with the portal via natural language.</p>

    <h2 class="section-heading">🔌 Built-In MCP Tools Reference</h2>
    <table class="guide-table">
      <tr>
        <th style="width: 30%;">MCP Tool Name</th>
        <th style="width: 35%;">Parameters</th>
        <th style="width: 35%;">Functional Capability</th>
      </tr>
      <tr>
        <td><span class="code-inline">search_items</span></td>
        <td><span class="code-inline">query, item_type, category</span></td>
        <td>Executes deep semantic search across all public lost &amp; found records.</td>
      </tr>
      <tr>
        <td><span class="code-inline">get_item_details</span></td>
        <td><span class="code-inline">item_id</span></td>
        <td>Retrieves complete metadata, custody location, and status for an item.</td>
      </tr>
      <tr>
        <td><span class="code-inline">analyze_image</span></td>
        <td><span class="code-inline">image_url / file_path</span></td>
        <td>Executes computer vision analysis extracting color palette and dimensions.</td>
      </tr>
      <tr>
        <td><span class="code-inline">check_matches</span></td>
        <td><span class="code-inline">item_id</span></td>
        <td>Invokes the multi-factor AI matching pipeline to find cross-pairings.</td>
      </tr>
    </table>

    <h2 class="section-heading">💬 Using the Natural Language Agent Endpoint</h2>
    <p>Developers and advanced users can communicate directly with the UniFound Agent endpoint at <span class="code-inline">POST /api/v1/agent/query</span>:</p>

    <div class="step-box" style="font-family: monospace; font-size: 8.5pt; background: #0f172a; color: #f8fafc;">
      # Sample Agent Request Payload<br>
      POST https://unifound-mqga.onrender.com/api/v1/agent/query<br>
      Content-Type: application/json<br>
      <br>
      {{<br>
      &nbsp;&nbsp;"prompt": "Did anyone find a brown leather Titan wallet near the Central Library yesterday?",<br>
      &nbsp;&nbsp;"session_id": "user-session-101"<br>
      }}<br>
      <br>
      # Agent Autonomous Execution:<br>
      1. Agent calls `search_items(query='Titan wallet', category='Wallets')`<br>
      2. Finds 1 item: ID #14 (Found at Library 1st floor desk)<br>
      3. Returns natural language summary with item ID, custody status, and link.
    </div>

    <div class="alert-card success" style="margin-top: 14px;">
      <strong>🚀 Swagger Interactive Testing:</strong> Try the MCP tools directly in the interactive Swagger API sandbox at <strong><a href="https://unifound-mqga.onrender.com/docs">https://unifound-mqga.onrender.com/docs</a></strong> under the <em>"Agent Direct"</em> section.
    </div>

    <div class="footer-rule">
      <span>Parul University &bull; Faculty of IT &amp; Computer Science</span>
      <span>Page 9 of 10</span>
    </div>
  </div>
</div>
"""

    # ---------------- PAGE 10: FAQ & TROUBLESHOOTING ----------------
    html += """
<!-- PAGE 10: FAQ & TROUBLESHOOTING -->
<div class="page">
  <div class="border-box">
    <div class="header-rule">
      <span>UNIFOUND OPERATING MANUAL</span>
      <span>CHAPTER 8: FAQ &amp; SUPPORT</span>
    </div>

    <h1 class="manual-title">8. FAQ &amp; Troubleshooting Guide</h1>

    <h2 class="section-heading">❓ Frequently Asked Questions</h2>
    <div style="font-size: 9pt; line-height: 1.45;">
      <p><strong>Q1: What should I do immediately after losing an item?</strong><br>
      <em>A:</em> Post a <span class="badge badge-lost">LOST</span> report right away with specific physical traits and the estimated loss location. Regularly check your notifications for AI match alerts.</p>

      <p><strong>Q2: I found an item on campus. Should I keep it or hand it over?</strong><br>
      <em>A:</em> Report it on UniFound with a photo, then immediately hand the article over to the nearest departmental security desk or Central Security Office. Record the custody location in your report.</p>

      <p><strong>Q3: How long does claim approval take?</strong><br>
      <em>A:</em> Most claims are reviewed by campus security within 24 hours of submission. High-value electronics requiring serial number inspection may take up to 48 hours.</p>

      <p><strong>Q4: Why was my claim rejected?</strong><br>
      <em>A:</em> Claims are rejected if the provided description or ownership proof contradicts the physical article. You may resubmit with additional documentation or visit the security desk in person.</p>
    </div>

    <h2 class="section-heading">🛠️ Troubleshooting Common Issues</h2>
    <table class="guide-table">
      <tr>
        <th style="width: 30%;">Issue</th>
        <th style="width: 70%;">Solution</th>
      </tr>
      <tr>
        <td><strong>Cannot log in / Invalid credentials</strong></td>
        <td>Verify your email and password casing. If forgotten, contact campus security or use password reset.</td>
      </tr>
      <tr>
        <td><strong>Photo upload fails</strong></td>
        <td>Ensure your image file is in JPG, PNG, or WEBP format and does not exceed 10 MB.</td>
      </tr>
      <tr>
        <td><strong>Session expired alert</strong></td>
        <td>Security tokens expire after 24 hours of inactivity. Simply re-login at <span class="code-inline">/login</span>.</td>
      </tr>
      <tr>
        <td><strong>Admin Dashboard not visible</strong></td>
        <td>Admin features are restricted to accounts with the <span class="code-inline">ADMIN</span> role. Log in with the official administrator credentials.</td>
      </tr>
    </table>

    <div class="step-box" style="margin-top: 10px; text-align: center; background: #f8fafc;">
      <strong style="color: #1e1b4b; font-size: 10.5pt;">📞 Campus Help Desk &amp; Support Contact</strong><br>
      <span style="font-size: 9pt; color: #64748b;">
        Parul University Central Security &amp; Student Affairs &bull; Vadodara, Gujarat<br>
        Email: <strong>support@unifound-campus.edu</strong> &bull; Portal: <strong>https://unifound-app.vercel.app</strong>
      </span>
    </div>

    <div class="footer-rule">
      <span>Parul University &bull; Faculty of IT &amp; Computer Science</span>
      <span>Page 10 of 10</span>
    </div>
  </div>
</div>
</body>
</html>"""
    return html


def build_pdf():
    print("Generating User Manual HTML...")
    html_content = generate_user_manual_html()
    
    html_path = Path(__file__).parent / "user_manual.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved {html_path}")

    pdf_path = Path(__file__).parent / "UNIFOUND_USER_MANUAL.pdf"
    
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    
    edge_exe = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_exe = p
            break
            
    if not edge_exe:
        print("ERROR: Microsoft Edge not found.")
        return

    print("Converting User Manual to PDF via Microsoft Edge headless...")
    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        f"file:///{html_path.resolve()}"
    ]
    
    subprocess.run(cmd, check=True)
    
    if pdf_path.exists():
        size_kb = pdf_path.stat().st_size / 1024
        print(f"SUCCESS: Generated {pdf_path} ({size_kb:.2f} KB)")
        
        # Copy to Downloads and Desktop
        home = os.path.expanduser("~")
        downloads = os.path.join(home, "Downloads", "UNIFOUND_USER_MANUAL.pdf")
        desktop = os.path.join(home, "OneDrive", "Desktop", "UNIFOUND_USER_MANUAL.pdf")
        
        try:
            shutil.copy2(pdf_path, downloads)
            print(f"Copied to Downloads: {downloads}")
        except Exception as e:
            print(f"Downloads copy note: {e}")
            
        try:
            shutil.copy2(pdf_path, desktop)
            print(f"Copied to Desktop: {desktop}")
        except Exception as e:
            print(f"Desktop copy note: {e}")

if __name__ == "__main__":
    build_pdf()
