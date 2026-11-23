"""Typeset the eight-page research paper from its manuscript and two attributed figures."""
from pathlib import Path
import re
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
    txt=escape(txt)
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
    return textblock(c,body,x,y,COL,size,size*1.24,justify=True,paint=paint)


def figure(c,page,top):
    """Draw in a local coordinate system; return the bottom of the caption."""
    height={1:105,2:140,3:120,5:239,6:150,7:135,8:93}[page]
    y=top-height
    c.saveState()
    c.translate(L,y)
    if page==1:
        tag(c,0,91,'A matched evaluation of one agent',11,font='TNR-Bold')
        blocks=[('Conditions','Task pair','same goal, one change'),('Execution','Agent trace','actions and evidence'),('Outcome','Task score','correct or incomplete'),('Process','Decision audit','justified or unsupported')]
        for i,(a,b,d) in enumerate(blocks):
            x=i*131
            box(c,x,10,124,66,TINT[i])
            tag(c,x+8,58,a.upper(),7.4,ACC[i],'Helvetica-Bold')
            tag(c,x+8,39,b,13,INK,'TNR-Bold')
            tag(c,x+8,21,d,8,INK)
            if i<3: line(c,x+124,42,x+131,42,ACC[i])
    elif page==2:
        tag(c,0,126,'One goal, three shifts',11,font='TNR-Bold')
        box(c,0,40,126,52,TINT[0])
        tag(c,9,71,'Reference task',12,INK,'TNR-Bold')
        tag(c,9,54,'Locate a named record',8.7)
        for i,(a,b) in enumerate([('Interface','Move or rename the search control'),('Evidence','Replace a text label with a visual cue'),('Composition','Require a second lookup before selection')]):
            yy=87-39*i
            line(c,126,66,157,66)
            line(c,157,66,157,yy+14)
            line(c,157,yy+14,176,yy+14)
            box(c,176,yy,338,29,TINT[i+1])
            tag(c,185,yy+10,a,10,ACC[i+1],'Helvetica-Bold')
            tag(c,274,yy+10,b,9)
    elif page==3:
        tag(c,0,103,'AgentSynth success at two reported difficulty levels',11,font='TNR-Bold')
        for i,(label,val) in enumerate([('Level 1',18),('Level 6',4)]):
            yy=68-31*i
            tag(c,0,yy+3,label,10)
            c.setFillColor(C(TINT[i])); c.rect(86,yy,350,17,0,1)
            c.setFillColor(C(ACC[i])); c.rect(86,yy,350*val/20,17,0,1)
            tag(c,450,yy+1,f'{val}%',13,ACC[i],'Helvetica-Bold')
        for v in [0,5,10,15,20]:
            xx=86+v*17.5
            line(c,xx,28,xx,24)
            tag(c,xx-3,11,f'{v}%',8,MUTED)
    elif page==5:
        p=ROOT/'figures/source-20.png'
        c.drawImage(ImageReader(p),0,0,width=W,height=height,preserveAspectRatio=True,anchor='c',mask='auto')
    elif page==6:
        tag(c,0,137,'Audit of a cross-source join',11,font='TNR-Bold')
        tag(c,128,113,'Check observed',10,ACC[0],'Helvetica-Bold')
        tag(c,332,113,'Check missing',10,ACC[3],'Helvetica-Bold')
        for i,(row,words) in enumerate([('Correct answer',['Supported match','Accidental match possible']),('Incorrect answer',['Inspect later operations','Inspect join and calculation'])]):
            yy=66-48*i
            tag(c,0,yy+14,row,10,INK,'TNR-Bold')
            for j,word in enumerate(words):
                xx=119+200*j
                box(c,xx,yy,194,39,TINT[i*2+j]); tag(c,xx+9,yy+15,word,10)
    elif page==7:
        tag(c,0,120,'Twenty eligible tasks per agent',11,font='TNR-Bold')
        for i,nums in enumerate([(10,6,4),(14,2,4)]):
            yy=82-31*i
            tag(c,0,yy+3,'Agent '+('A' if i==0 else 'B'),10,INK,'TNR-Bold')
            xx=71
            for k,v in enumerate(nums):
                ww=21.5*v
                c.setFillColor(C(ACC[[0,2,3][k]])); c.rect(xx,yy,ww,21,0,1)
                tag(c,xx+ww/2-4,yy+6,str(v),10,'#FFFFFF','Helvetica-Bold')
                xx+=ww
        for x,idx,label in [(0,0,'Correct + verified'),(175,2,'Correct + unverified'),(362,3,'Incorrect')]:
            box(c,x,18,10,10,ACC[idx]); tag(c,x+16,19,label,9)
    elif page==8:
        tag(c,0,77,'Publication records in the review',11,font='TNR-Bold')
        xx=0
        for i,(v,label) in enumerate([(6,'Lab reports and preprints'),(3,'ICLR'),(11,'ACL-family proceedings')]):
            ww=W*v/20
            c.setFillColor(C(ACC[i])); c.rect(xx,35,ww-2,28,0,1)
            tag(c,xx+7,44,str(v),12,'#FFFFFF','Helvetica-Bold')
            tag(c,xx,19,label,8.3)
            xx+=ww
    c.restoreState()
    caps={
      1:'Authors’ framework. A change in conditions is interpreted alongside two observations from the same run: what the agent accomplished and which evidence supported its decision. Based on [5, 12, 19].',
      2:'Proposed paired variants of a lookup task. Each branch starts from the same reference task. The comparison tests a different aspect of transfer in each branch [1, 3, 4].',
      3:'Authors’ chart of the two endpoint values reported by Xie et al. [9]. The horizontal scale runs from 0% to 20%. The underlying study reports results for its own generated tasks and evaluated agents.',
      5:'DAB setup and example agent trace. Ma et al. [20], Fig. 1, p. 42652. Reproduced from the paper, cropped to the figure panels. © 2026 ACL, CC BY 4.0.',
      6:'Authors’ outcome and process grid, informed by [19, 20]. Cell descriptions give candidate explanations for a single episode. The example assumes the trace is complete and the check applies.',
      7:'Authors’ illustrative counts. The teal segment counts tasks meeting both criteria. The amber segment counts correct answers without an observed check. These are hypothetical runs.',
      8:'Authors’ count of the reviewed records [1–20], grouped by the version cited. A proceedings paper is counted once even if an earlier preprint exists.'}
    return caption(c,page,caps[page],L,y-3,W)


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
    for y,txt,font,size in [(739,title,'TNR-Bold',23),(717,'A Framework for Evaluating Capability, Transfer, and Reliability in AI Agents','TNR',12),(694,'Author:'+FIRST_AUTHOR,'TNR-Bold',11),(678,'Co-Author:'+SECOND_AUTHOR,'TNR-Bold',11),(660,'23 November 2026','TNR',9.5)]:
        c.setFont(font,size);c.drawCentredString(306,y,txt)
    return 641


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
        figspace={1:105,2:140,3:120,5:239,6:150,7:135}[page]
        for size in [11.5,11.25,11,10.75,10.5,10.25,10,9.75]:
            upper=min(section(c,p,L,top,size,False) for p in parts[:2])
            lower=min(section(c,p,L,0,size,False) for p in parts[2:])
            room=upper-figspace-36+lower-53
            if room>=24:
                break
        gap=max(9,min(room/2,32))
        section(c,parts[0],L,top,size); section(c,parts[1],COL2,top,size)
        col_top=figure(c,page,upper-gap)-gap
        bottom=min(section(c,parts[2],L,col_top,size),section(c,parts[3],COL2,col_top,size))
    if bottom<45:
        raise ValueError(f'Page {page} ends at {bottom:.1f}')
    print(f'Page {page} ends at {bottom:.1f}')


def references(c,top):
    y=figure(c,8,top)-14
    author_override={6:'Renmin University of China and ByteDance Seed',18:'Bogavelli, Subramani and Sharma'}
    for i,s in enumerate(SOURCES):
        if i in (0,10): yy=y
        x=L if i<10 else COL2
        c.bookmarkHorizontalAbsolute('ref'+str(i+1),yy)
        title=s['title'] if i!=15 else 'OS-Symphony: A Holistic Framework for Robust and Generalist Computer-Using Agent'
        author=author_override.get(i+1,s['authors'])
        venue=(['Google DeepMind','arXiv','arXiv','Position paper','arXiv','arXiv']+['ICLR']*3+['Findings of ACL']*3+['EMNLP']*3+['ACL','Findings of EMNLP','AACL','Findings of EACL','EMNLP'])[i]
        tag(c,x,yy-10,str(i+1).zfill(2),8.6,ACC[1],'Helvetica-Bold')
        punctuation='' if title.endswith(('?', '.', '!')) else '.'
        txt=f'{author} (2026). {title}{punctuation} {venue}.'
        end=textblock(c,txt,x+20,yy,COL-20,10,12)
        c.linkURL(s['url'],(x, end,x+COL,yy),relative=0,thickness=0)
        yy=end-7
        if yy<44: raise ValueError('References overflow')
    tag(c,L,49,'Select a reference to open its official record.',8,MUTED,'TNR-Italic')


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
