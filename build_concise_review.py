"""Typeset the eight-page research paper from its manuscript, reference records and credited figures."""
from PIL import Image as PILImage
import re
import json
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from build_academic_review import ROOT, OUT, SOURCES, AUTHORS, FIRST_AUTHOR, SECOND_AUTHOR

TARGET = OUT / "AGI_Research_Paper_8_pages.pdf"
L, R, W, COL, COL2 = 47, 565, 518, 249, 316
INK, MUTED, RULE = '#17252E', '#455969', '#AFC2CB'
TINT = ['#E4F2F0', '#E8EFFB', '#FCEED8', '#F2E7F2']
ACC = ['#156A64', '#30588B', '#895313', '#78446F']
C = colors.HexColor


def tag(c,x,y,t,sz=9,color=INK,font='Helvetica'):
    c.setFont(font,sz)
    c.setFillColor(C(color))
    c.drawString(x,y,t)


def line(c,x,y,xx,yy,color=RULE,width=0.65):
    c.setStrokeColor(C(color))
    c.setLineWidth(width)
    c.line(x,y,xx,yy)


def box(c,x,y,w,h,fill):
    c.setFillColor(C(fill))
    c.roundRect(x,y,w,h,4,stroke=0,fill=1)


def textblock(c,txt,x,y,width,size=10.8,leading=13.4,font='TNR',justify=False,paint=True):
    style=ParagraphStyle('paper',fontName=font,fontSize=size,leading=leading,textColor=C(INK),
                         alignment=TA_JUSTIFY if justify else TA_LEFT)
    txt=escape(txt).replace('CC BY 4.0','<link href="https://creativecommons.org/licenses/by/4.0/" color="#235481">CC BY 4.0</link>')
    def link(m):
        ids=[int(k) for k in m[1].split(', ')]
        return '['+', '.join(f'<link href="#ref{i}" color="#235481">{i}</link>' for i in ids)+']'
    txt=re.sub(r'\[([0-9]+(?:, [0-9]+)*)\]',link,txt)
    p=Paragraph(txt,style)
    _,h=p.wrap(width,800)
    if paint:
        p.drawOn(c,x,y-h)
    return y-h


def section(c,part,x,y,size,paint=True):
    heading,body=part
    y=textblock(c,heading,x,y,COL,12.1,14.8,'TNR-Bold',paint=paint)-4
    end=textblock(c,body,x,y,COL,size,size*1.24,justify=True,paint=paint)
    if heading=='Abstract':
        end=textblock(c,'Keywords: artificial general intelligence, AI agents, transfer learning, reliability, process evaluation',x,end-4,COL,9,10.2,'TNR-Italic',paint=paint)
    return end


FIGURES = {
    1: (18, 172, "AgentArch links two enterprise workflows to architecture settings and scoring decisions. Bogavelli et al. [18], Fig. 1."),
    2: (17, 214, "Role-Agent compares static, synthetic and jointly evolving environments. Wang et al. [17], Fig. 1."),
    3: (10, 240, "Building a tool environment and an executable task. Fang et al. [10], Fig. 1."),
    5: (20, 239, "DAB setup and a trace linking book and review records across databases. Ma et al. [20], Fig. 1."),
    6: (19, 225, "Planner, assistant and tool calls in an example agent workflow. Gritta et al. [19], Fig. 1. The annotation at right applies our audit to the database case."),
    8: (12, 145, "Application-specific benchmarks in the survey taxonomy. Yehudai et al. [12], Fig. 1, excerpt."),
}
NOTES = {
    2: ("Reading the three settings", [
        ("Static", "The agent explores a fixed environment. Sparse feedback can leave a mistaken procedure uncorrected."),
        ("Synthetic", "Generating a new setting widens exposure. A shared generator can still repeat the same assumptions."),
        ("Joint evolution", "The agent and environment change together. Reserve an independent task to test whether a learned procedure transfers.")]),
    6: ("Worked trace annotation", [
        ("Plan", "Retrieve titles and ratings. Record the identifier used by each source before combining records."),
        ("Tool observation", "If two rows share a title but refer to different editions, a title match alone cannot establish identity."),
        ("Review decision", "Mark the check as satisfied only when the trace resolves the ambiguity or requests clarification.")]),
}


def figure(c,page,top):
    if page in (3,8):
        if page==3:
            rows=[('Tool documents','Names, parameters and signatures','Connect tools that share parameters.'),
                  ('Tool graph','Domain clusters and a tool set','Select a related group of callable tools.'),
                  ('Environment','Grounding functions and state','Specify how a call reads or modifies state.'),
                  ('Task instance','Intent, initial state and target','Evaluate the resulting state after execution.')]
            title='From a tool schema to an executable evaluation task'
            credit='Redrawn from Fang et al. [10], Fig. 1 (CC BY 4.0). The rows follow construction order. Labels summarize the operations.'
            h=32
        else:
            rows=[('Web','WebShop, Mind2Web'),('Software engineering','SWE-bench, SWE-bench Verified'),('Scientific','ScienceAgentBench, PeerBench'),('Conversational','τ-bench, τ²-bench')]
            title='Agent evaluation by application domain'
            credit='Redrawn from Yehudai et al. [12], Fig. 1 (CC BY 4.0). Selected branches and benchmark names are typeset at reading size.'
            h=20
        tag(c,L,top-12,title,12,font='TNR-Bold')
        if page==3:
            # Pair the published structure with large, selectable labels for its subpanels.
            with PILImage.open(ROOT/'figures/source-10.png') as source:
                detail=source.crop((282,450,737,597))
                c.drawImage(ImageReader(detail),L,top-175,305,130,preserveAspectRatio=True,anchor='c')
            x=L+318
            yy=top-24
            for idx,(stage,feature,action) in enumerate(rows):
                tag(c,x,yy-9,stage,11.2,ACC[idx],'TNR-Bold')
                yy=textblock(c,action,x,yy-13,W-318,10.2,12.3)-10
            yy=min(yy,top-178)
            credit='Tool sequence from Fang et al. [10], Fig. 1, CC BY 4.0. The four numbered calls are enlarged from the original. The reading guide summarizes the construction process. Select the figure for the complete diagram.'
            c.linkURL(SOURCES[9]['url'].rstrip('/')+'.pdf#page=4',(L,top-177,L+305,top-38),relative=0,thickness=0)
        else:
            root_x=L+6
            mid=top-63
            tag(c,root_x,mid,'Application-specific',10,ACC[0],'TNR-Bold')
            tag(c,root_x,mid-13,'agent evaluation',10,ACC[0],'TNR-Bold')
            line(c,L+93,mid-1,L+111,mid-1)
            line(c,L+111,top-32,L+111,top-98)
            for idx,(domain,benchmarks) in enumerate(rows):
                yy=top-32-22*idx
                line(c,L+111,yy,L+123,yy)
                box(c,L+123,yy-9,123,18,TINT[idx])
                tag(c,L+130,yy-4,domain,10.4,ACC[idx],'TNR-Bold')
                line(c,L+247,yy,L+263,yy)
                tag(c,L+270,yy-4,benchmarks,10.3,font='TNR')
            yy=top-110
        return caption(c,page,credit,L,yy-4,W)
    if page == 7:
        # A concrete counterexample: one ambiguous title, two candidate identifiers.
        height=174
        y=top-height
        tag(c,L,top-11,'Worked example: tracing the identity of a book',12,font='TNR-Bold')
        for j,(name,rows) in enumerate([
            ('Catalogue', ['ID      TITLE           EDITION','51      Ember           2018','72      Ember           2022']),
            ('Review record', ['REF     TITLE           RATING','E72     Ember           5.0'])]):
            x=L+j*265
            box(c,x,top-90,250,67,TINT[j])
            tag(c,x+9,top-39,name,10,ACC[j],'Helvetica-Bold')
            for k,row in enumerate(rows): tag(c,x+9,top-54-12*k,row,8.2,INK,'Courier')
        line(c,L+124,top-90,L+124,top-101)
        line(c,L+390,top-90,L+390,top-101)
        for j,(name,detail) in enumerate([
            ('Title match','Both catalogue rows match. The edition is ambiguous.'),
            ('Verified key mapping','If the source documents E72 → 72, select the 2022 edition.')]):
            x=L+j*265
            tag(c,x,top-119,name,10,ACC[3-j],'Helvetica-Bold')
            textblock(c,detail,x,top-126,COL,10,12)
        return caption(c,7,'Illustrative records created for this paper. A correct title conceals a choice between two editions. The score below counts whether the trace establishes the mapping.',L,y+8,W)
    source,height,credit=FIGURES[page]
    bottom=top-height
    w=COL if page in NOTES else W
    im=ImageReader(ROOT/f'figures/source-{source}.png')
    c.drawImage(im,L,bottom,width=w,height=height,preserveAspectRatio=True,anchor='c',mask='auto')
    if page in NOTES:
        title,notes=NOTES[page]
        yy=top-12
        tag(c,COL2,yy,title,12,font='TNR-Bold')
        yy-=18
        for name,note in notes:
            tag(c,COL2,yy,name,10,ACC[0],'Helvetica-Bold')
            yy=textblock(c,note,COL2,yy-5,COL,10.5,12.6)-15
    return caption(c,page,credit+' Source artwork cropped from the paper, © 2026 ACL, CC BY 4.0.',L,bottom-3,W)


def caption(c,i,txt,x,top,width):
    return textblock(c,f'Figure {i}.  {txt}',x,top,width,9,11,'TNR-Italic')


def start(c,page,title):
    c.bookmarkPage(f'page{page}')
    c.addOutlineEntry(title,f'page{page}',0)
    if page>1:
        tag(c,L,757,'AGI RESEARCH REVIEW',8,MUTED,'Helvetica-Bold')
        name=FIRST_AUTHOR if page%2 else SECOND_AUTHOR
        c.setFont('TNR',8); c.drawRightString(R,757,name.upper())
        line(c,L,749,R,749)
        c.setFont('TNR-Bold',21); c.setFillColor(C(INK)); c.drawString(L,715,title)
        return 694
    c.setFillColor(C(INK))
    for y,txt,font,size in [(755,title,'TNR-Bold',23),(734,'A Framework for Evaluating Capability, Transfer, and Reliability in AI Agents','TNR',12),(714,'Author:'+FIRST_AUTHOR,'TNR-Bold',11),(674,'Co-Author:'+SECOND_AUTHOR,'TNR-Bold',11),(636,'23 November 2026','TNR',9.5)]:
        c.setFont(font,size);c.drawCentredString(306,y,txt)
    for yy,addr in [(690,'rashmiranjanabc241947@gmail.com'),(650,'vidya.mohanty@gmail.com')]:
        c.setFont('TNR',9)
        c.drawCentredString(306,yy,addr)
        c.linkURL('mailto:'+addr,(220,yy-2,392,yy+9),relative=0,thickness=0)
    return 622


def finish(c,page):
    line(c,L,38,R,38)
    tag(c,L,24,'Independent literature synthesis',8,MUTED,'TNR-Italic')
    c.setFont('TNR',8); c.drawRightString(R,24,str(page))
    c.showPage()


def body_page(c,page,top,parts):
    if page==4:
        image_top=top
        im=ImageReader(ROOT/'figures/source-16.png')
        iw,ih=im.getSize()
        h=COL*ih/iw
        c.drawImage(im,L,image_top-h,COL,h,mask='auto')
        left_end=caption(c,4,'Existing memory and retrieval mechanisms. Yang et al. [16], Fig. 1, p. 22300. Reproduced from the paper, cropped to the diagram. © 2026 ACL, CC BY 4.0.',L,image_top-h-5,COL)
        yy=section(c,parts[0],COL2,top,11.1)-13
        right_end=section(c,parts[1],COL2,yy,11.1)
        top=min(left_end,right_end)-22
        bottom=min(section(c,parts[2],L,top,11.1),section(c,parts[3],COL2,top,11.1))
        y=bottom-25
        tag(c,L,y,'Table 1.  Worked trace for the interruption test',11,INK,'TNR-Bold')
        for j,(stage,observed,scored) in enumerate([
            ('Moment','Evidence available','Decision to record'),
            ('Pause','Saved milestone names account A','Record the account and timestamp'),
            ('Resume','Visible selector now shows account B','Compare the selector with the milestone'),
            ('Next action','Task still specifies account A','Restore A and verify before proceeding')
        ]):
            yy=y-22-j*21
            if j==0: box(c,L,yy-5,W,19,TINT[0])
            else: line(c,L,yy-6,R,yy-6)
            for x,s in zip((L+6,L+85,L+305),(stage,observed,scored)):
                tag(c,x,yy,s,9,INK,'TNR-Bold' if j==0 else 'TNR')
        bottom=yy-7
    else:
        # Choose the largest common body size that leaves space for the figure and its caption.
        figspace={3:195,7:174}.get(page,FIGURES.get(page,(None,174))[1])
        for size in [11.5,11.25,11,10.75,10.5,10.25,10,9.75]:
            upper=min(section(c,p,L,top,size,False) for p in parts[:2])
            lower=min(section(c,p,L,0,size,False) for p in parts[2:])
            room=upper-figspace-36+lower-53
            if room>=24:
                break
        gap=max(6,min(room/2,10))
        section(c,parts[0],L,top,size); section(c,parts[1],COL2,top,size)
        col_top=figure(c,page,upper-gap)-gap
        bottom=min(section(c,parts[2],L,col_top,size),section(c,parts[3],COL2,col_top,size))
    if bottom<45:
        raise ValueError(f'Page {page} ends at {bottom:.1f}')
    print(f'Page {page} ends at {bottom:.1f}')


def references(c,top):
    y=figure(c,8,top)-9
    records=json.loads((ROOT/'concise_references.json').read_text())
    for i,r in enumerate(records):
        if i in (0,10): yy=y
        x=L if i<10 else COL2
        c.bookmarkHorizontalAbsolute('ref'+str(i+1),yy)
        tag(c,x,yy-9,f'{i+1:02}',8.5,ACC[1],'Helvetica-Bold')
        title=r['title'].rstrip('.')
        mark='' if title.endswith('?') else '.'
        entry=f"{r['author']} ({r['year']}). {title}{mark} {r['venue']}."
        end=textblock(c,entry,x+17,yy,COL-17,9,10.25)
        end=textblock(c,r['label'],x+17,end-1,COL-17,8.4,9.4,'TNR-Italic')
        c.linkURL(r['url'],(x,end,x+COL,yy),relative=0,thickness=0)
        yy=end-4
        if end<43: raise ValueError(f'Reference {i+1} ends at {end}')



def build_document():
    c=Canvas(str(TARGET),pagesize=(612,792),pageCompression=1)
    c.setAuthor(AUTHORS); c.setTitle('General Intelligence as a Research Program')
    c.setSubject('An eight-page literature review and proposed agent evaluation protocol')
    sections=re.split(r'^# ',(ROOT/'concise_paper.md').read_text(),flags=re.M)[1:]
    for i,chunk in enumerate(sections,1):
        title,*sections_text=re.split(r'^## ',chunk,flags=re.M)
        top=start(c,i,title.strip())
        if i==8: references(c,top)
        else: body_page(c,i,top,[s.strip().split('\n',1) for s in sections_text])
        finish(c,i)
    c.save()
    return TARGET


if __name__=='__main__':
    print(build_document())
