"""
Génère des rapports de matchs PDF pour tester le RAG FootPress AI
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import os

OUTPUT_DIR = r"D:\projects\estiam\AZURE AI\finalproject\sample_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()
GREEN = colors.HexColor("#16a34a")
DARK = colors.HexColor("#111827")
GRAY = colors.HexColor("#6b7280")

title_style   = ParagraphStyle("Title2",   parent=styles["Title"],   textColor=DARK,  fontSize=20, spaceAfter=6)
h1_style      = ParagraphStyle("H1",       parent=styles["Heading1"], textColor=GREEN, fontSize=13, spaceAfter=4)
h2_style      = ParagraphStyle("H2",       parent=styles["Heading2"], textColor=DARK,  fontSize=11, spaceAfter=3)
body_style    = ParagraphStyle("Body",     parent=styles["Normal"],   fontSize=10,     leading=15,  spaceAfter=6)
meta_style    = ParagraphStyle("Meta",     parent=styles["Normal"],   fontSize=9,      textColor=GRAY, spaceAfter=10)
caption_style = ParagraphStyle("Caption",  parent=styles["Normal"],   fontSize=9,      textColor=GRAY, alignment=1)

def build(filename, story):
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    doc.build(story)
    print(f"  OK {filename}")

def sep():
    return [HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"), spaceAfter=8, spaceBefore=4)]


# ─────────────────────────────────────────────
# PDF 1 — PSG vs Bayern Munich (Ligue des Champions)
# ─────────────────────────────────────────────
def pdf_psg_bayern():
    s = []
    s.append(Paragraph("RAPPORT DE MATCH", meta_style))
    s.append(Paragraph("PSG 3 – 1 Bayern Munich", title_style))
    s.append(Paragraph("Ligue des Champions UEFA — Quarts de finale retour | 9 avril 2026 | Parc des Princes, Paris", meta_style))
    s += sep()

    s.append(Paragraph("Résumé du match", h1_style))
    s.append(Paragraph(
        "Le Paris Saint-Germain a réalisé une performance magistrale au Parc des Princes pour éliminer le Bayern Munich "
        "et se qualifier pour les demi-finales de la Ligue des Champions. Grâce à un doublé de Ousmane Dembélé et un but "
        "de Vitinha, les Parisiens ont renversé la situation après avoir encaissé l'ouverture du score bavaroise dès la 7e minute. "
        "Une victoire 3-1 qui envoie Paris en demi-finale pour la première fois depuis 2021.",
        body_style))

    s.append(Paragraph("Buts et événements clés", h1_style))
    data = [
        ["Min", "Buteur", "Club", "Type", "Score"],
        ["7'",  "Harry Kane",       "Bayern Munich", "Pénalty",   "0 – 1"],
        ["23'", "Ousmane Dembélé",  "PSG",           "Tête",      "1 – 1"],
        ["51'", "Vitinha",          "PSG",           "Frappe lointaine", "2 – 1"],
        ["78'", "Ousmane Dembélé",  "PSG",           "Contre-attaque",   "3 – 1"],
    ]
    t = Table(data, colWidths=[1.5*cm, 5*cm, 4*cm, 4.5*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GREEN),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    s.append(t)
    s.append(Spacer(1, 0.4*cm))

    s.append(Paragraph("Statistiques du match", h1_style))
    stats = [
        ["Statistique",          "PSG",   "Bayern Munich"],
        ["Possession (%)",       "54",    "46"],
        ["Tirs cadrés",          "7",     "3"],
        ["Tirs totaux",          "14",    "9"],
        ["Passes réussies",      "487",   "412"],
        ["Corners",              "6",     "4"],
        ["Fautes commises",      "11",    "15"],
        ["Cartons jaunes",       "2",     "3"],
        ["Distance parcourue (km)", "108", "105"],
    ]
    t2 = Table(stats, colWidths=[7*cm, 3*cm, 4.5*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",      (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    s.append(t2)
    s.append(Spacer(1, 0.4*cm))

    s.append(Paragraph("Performances individuelles", h1_style))
    s.append(Paragraph("<b>Ousmane Dembélé (PSG) — Homme du match :</b> 2 buts, 1 passe décisive, 4 dribbles réussis, "
                        "noté 9.2/10. L'ailier français a été omniprésent sur le flanc droit, créant le danger à chaque accélération.", body_style))
    s.append(Paragraph("<b>Vitinha (PSG) :</b> 1 but, 94% de passes réussies, 8 ballons récupérés. "
                        "Le milieu portugais a contrôlé le tempo du match en seconde période.", body_style))
    s.append(Paragraph("<b>Gianluigi Donnarumma (PSG) :</b> 3 arrêts décisifs dont une parade réflexe sur frappe de Gnabry à la 65e. "
                        "Le gardien italien a été décisif pour maintenir l'avantage parisien.", body_style))
    s.append(Paragraph("<b>Harry Kane (Bayern) :</b> 1 but (pénalty), 5 frappes dont 2 cadrées. "
                        "Le capitaine anglais a eu peu de ballons exploitables face à une défense parisienne bien organisée.", body_style))

    s.append(Paragraph("Analyse tactique", h1_style))
    s.append(Paragraph(
        "Le PSG de Luis Enrique a évolué dans un 4-3-3 compact, avec une pression haute qui a mis le Bayern en difficulté "
        "dans la construction. Le pressing organisé a généré plusieurs récupérations hautes, dont celle qui a conduit au but "
        "de Vitinha en début de seconde période. Le Bayern, privé de Müller (blessé) et de Goretzka (suspendu), n'a jamais "
        "trouvé les solutions pour contourner le bloc parisien. Munich a fini à 10 contre 11 après l'expulsion de Kimmich à la 82e minute.",
        body_style))

    s.append(Paragraph("Composition des équipes", h1_style))
    s.append(Paragraph("<b>PSG :</b> Donnarumma — Hakimi, Marquinhos, Pacho, Mendes — Vitinha, Zaire-Emery, Fabian Ruiz — "
                        "Dembélé, Ramos, Barcola", body_style))
    s.append(Paragraph("<b>Bayern Munich :</b> Neuer — Laimer, Upamecano, Kim Min-Jae, Davies — Kimmich, Pavlovic — "
                        "Gnabry, Musiala, Sané — Kane", body_style))

    s += sep()
    s.append(Paragraph("Rapport rédigé par la rédaction FootPress AI • 9 avril 2026", caption_style))
    build("match_psg_bayern_ucl_2026.pdf", s)


# ─────────────────────────────────────────────
# PDF 2 — Real Madrid vs Arsenal (Ligue des Champions)
# ─────────────────────────────────────────────
def pdf_real_arsenal():
    s = []
    s.append(Paragraph("RAPPORT DE MATCH", meta_style))
    s.append(Paragraph("Real Madrid 1 – 2 Arsenal FC", title_style))
    s.append(Paragraph("Ligue des Champions UEFA — Demi-finale aller | 29 avril 2026 | Santiago Bernabéu, Madrid", meta_style))
    s += sep()

    s.append(Paragraph("Résumé du match", h1_style))
    s.append(Paragraph(
        "Arsenal a créé l'exploit au Santiago Bernabéu en s'imposant 2-1 face au Real Madrid lors du premier match de "
        "demi-finale de Ligue des Champions. Les Gunners, menés par un Bukayo Saka en état de grâce, ont renversé l'ouverture "
        "du score de Vinicius Jr grâce à des buts de Martin Odegaard (50e) et Gabriel Martinelli (73e). "
        "Un résultat historique qui relance totalement la qualification pour la finale.",
        body_style))

    s.append(Paragraph("Buts et événements clés", h1_style))
    data = [
        ["Min", "Buteur",            "Club",       "Type",              "Score"],
        ["31'", "Vinicius Jr",       "Real Madrid", "Frappe enroulée",  "1 – 0"],
        ["50'", "Martin Odegaard",   "Arsenal",    "Coup franc direct", "1 – 1"],
        ["73'", "Gabriel Martinelli","Arsenal",    "Contre-attaque",    "1 – 2"],
    ]
    t = Table(data, colWidths=[1.5*cm, 5*cm, 4*cm, 4.5*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GREEN),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    s.append(t)
    s.append(Spacer(1, 0.4*cm))

    s.append(Paragraph("Statistiques du match", h1_style))
    stats = [
        ["Statistique",             "Real Madrid", "Arsenal"],
        ["Possession (%)",          "61",          "39"],
        ["Tirs cadrés",             "4",           "5"],
        ["Tirs totaux",             "17",          "11"],
        ["Expected Goals (xG)",     "1.8",         "1.2"],
        ["Passes réussies",         "601",         "378"],
        ["Duels gagnés (%)",        "44",          "56"],
        ["Cartons jaunes",          "2",           "4"],
        ["Kilomètres parcourus",    "107",         "113"],
    ]
    t2 = Table(stats, colWidths=[7*cm, 3.5*cm, 3.5*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",      (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    s.append(t2)
    s.append(Spacer(1, 0.4*cm))

    s.append(Paragraph("Performances individuelles", h1_style))
    s.append(Paragraph("<b>Bukayo Saka (Arsenal) — Homme du match :</b> 1 passe décisive, 6 dribbles réussis sur 7 tentatives, "
                        "87 touches de balle, noté 9.0/10. L'ailier anglais a rendu Ferland Mendy complètement impuissant tout au long du match.", body_style))
    s.append(Paragraph("<b>Martin Odegaard (Arsenal) :</b> 1 but (coup franc), 91% de passes réussies, capitaine exemplaire. "
                        "Le Norvégien a dicté le jeu des Gunners balle au pied.", body_style))
    s.append(Paragraph("<b>David Raya (Arsenal) :</b> 6 arrêts dont une parade exceptionnelle sur tête de Bellingham à la 88e. "
                        "Le gardien espagnol a été le dernier rempart d'une défense londonienne héroïque.", body_style))
    s.append(Paragraph("<b>Jude Bellingham (Real Madrid) :</b> 2 tirs non cadrés, 87 ballons touchés mais peu de création. "
                        "L'Anglais a été bien muselé par le duo Partey-Rice au milieu.", body_style))

    s += sep()
    s.append(Paragraph("Rapport rédigé par la rédaction FootPress AI • 29 avril 2026", caption_style))
    build("match_real_arsenal_ucl_2026.pdf", s)


# ─────────────────────────────────────────────
# PDF 3 — Classement & stats Ligue 1 saison 2025-26
# ─────────────────────────────────────────────
def pdf_ligue1_stats():
    s = []
    s.append(Paragraph("BILAN DE MI-SAISON", meta_style))
    s.append(Paragraph("Ligue 1 — Saison 2025-2026", title_style))
    s.append(Paragraph("Journée 28 sur 34 | Données arrêtées au 1er avril 2026", meta_style))
    s += sep()

    s.append(Paragraph("Classement général", h1_style))
    classement = [
        ["#", "Club",             "J",  "V",  "N", "D", "BP", "BC", "Diff", "Pts"],
        ["1", "PSG",              "28", "21", "4", "3", "68", "28", "+40",  "67"],
        ["2", "AS Monaco",        "28", "18", "5", "5", "54", "31", "+23",  "59"],
        ["3", "OGC Nice",         "28", "16", "6", "6", "48", "33", "+15",  "54"],
        ["4", "Marseille",        "28", "15", "5", "8", "51", "38", "+13",  "50"],
        ["5", "Lens",             "28", "14", "7", "7", "43", "35", "+8",   "49"],
        ["6", "Lyon",             "28", "13", "6", "9", "46", "41", "+5",   "45"],
        ["7", "Rennes",           "28", "12", "6","10", "40", "39", "+1",   "42"],
        ["8", "Lille",            "28", "11", "8", "9", "38", "36", "+2",   "41"],
        ["18","Metz",             "28",  "5", "4","19", "24", "58", "-34",  "19"],
        ["19","Saint-Etienne",    "28",  "3", "6","19", "19", "61", "-42",  "15"],
        ["20","Bordeaux",         "28",  "2", "4","22", "18", "67", "-49",  "10"],
    ]
    t = Table(classement, colWidths=[1*cm, 4.5*cm, 1*cm, 1*cm, 1*cm, 1*cm, 1*cm, 1*cm, 1.5*cm, 1.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",   (0,1), (-1,1), "Helvetica-Bold"),
        ("BACKGROUND", (0,1), (-1,1), colors.HexColor("#dcfce7")),
        ("FONTSIZE",   (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,2), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",      (2,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    s.append(t)
    s.append(Spacer(1, 0.4*cm))

    s.append(Paragraph("Meilleurs buteurs", h1_style))
    buteurs = [
        ["#", "Joueur",              "Club",       "Buts", "Assists", "Matchs"],
        ["1", "Folarin Balogun",     "AS Monaco",  "19",   "7",       "27"],
        ["2", "Bradley Barcola",     "PSG",        "17",   "9",       "26"],
        ["3", "Mason Greenwood",     "Marseille",  "15",   "8",       "28"],
        ["4", "Elye Wahi",           "Nice",       "13",   "5",       "25"],
        ["5", "Arnaud Kalimuendo",   "Rennes",     "12",   "6",       "28"],
        ["6", "Rayan Cherki",        "Lyon",       "11",   "11",      "27"],
    ]
    t2 = Table(buteurs, colWidths=[0.8*cm, 5*cm, 3.5*cm, 1.5*cm, 2*cm, 2*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GREEN),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",      (3,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    s.append(t2)
    s.append(Spacer(1, 0.4*cm))

    s.append(Paragraph("Faits marquants de la saison", h1_style))
    s.append(Paragraph("<b>PSG :</b> En route vers un 13e titre de champion. Le club parisien enchaîne 11 victoires consécutives "
                        "à domicile. Marquinhos, 32 ans, a prolongé son contrat jusqu'en 2028.", body_style))
    s.append(Paragraph("<b>Monaco :</b> Grande surprise de la saison. Balogun, prêté par Arsenal, est la révélation de Ligue 1. "
                        "Le club du Rocher joue sa meilleure saison depuis 2017.", body_style))
    s.append(Paragraph("<b>Bordeaux :</b> Retour difficile en Ligue 1 après deux saisons en L2. Le club girondin est en grand "
                        "danger de relégation avec seulement 10 points.", body_style))

    s += sep()
    s.append(Paragraph("Rapport statistique FootPress AI • Données Opta/SofaScore • Saison 2025-2026", caption_style))
    build("ligue1_stats_2025_2026.pdf", s)


# ─────────────────────────────────────────────
# PDF 4 — Profil joueur : Bradley Barcola
# ─────────────────────────────────────────────
def pdf_profil_barcola():
    s = []
    s.append(Paragraph("PROFIL JOUEUR", meta_style))
    s.append(Paragraph("Bradley Barcola — PSG", title_style))
    s.append(Paragraph("Ailier gauche | Francais | 23 ans | 1m80 | 72 kg | N.29", meta_style))
    s += sep()

    s.append(Paragraph("Biographie", h1_style))
    s.append(Paragraph(
        "Bradley Barcola est un ailier gauche formé à l'Olympique Lyonnais. Révélé au grand public lors de la saison 2022-2023 "
        "avec Lyon, il rejoint le Paris Saint-Germain en juillet 2023 pour 45 millions d'euros. Rapide, technique et efficace "
        "devant le but, il s'est imposé comme l'un des éléments clés du projet de Luis Enrique. International français, "
        "il a participé à l'Euro 2024 et à la Coupe du Monde 2026.",
        body_style))

    s.append(Paragraph("Statistiques saison 2025-2026 (Ligue 1)", h1_style))
    stats_perso = [
        ["Statistique",              "Valeur",  "Rang en L1"],
        ["Buts",                     "17",      "2e"],
        ["Passes décisives",         "9",       "3e"],
        ["Participation buts",       "26",      "1er"],
        ["Dribbles réussis/match",   "3.4",     "1er"],
        ["Tirs cadrés/match",        "1.8",     "2e"],
        ["Kilomètres parcourus/match","11.2",   "Top 5"],
        ["Duels gagnés (%)",         "58%",     "Top 10"],
        ["Note moyenne Sofascore",   "7.8",     "2e"],
    ]
    t = Table(stats_perso, colWidths=[7*cm, 3*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GREEN),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",      (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    s.append(t)
    s.append(Spacer(1, 0.4*cm))

    s.append(Paragraph("Palmarès", h1_style))
    s.append(Paragraph("<b>Avec le PSG :</b> Ligue 1 2023-24, 2024-25 (candidat 2025-26) | Coupe de France 2024 | Trophée des Champions 2024, 2025", body_style))
    s.append(Paragraph("<b>Avec la France :</b> Finaliste Euro 2024 | Coupe du Monde 2026 (en cours)", body_style))

    s.append(Paragraph("Analyse technique", h1_style))
    s.append(Paragraph(
        "Points forts : Vitesse de pointe exceptionnelle (estimée a 35,8 km/h), premier contrôle orienté, "
        "capacité à éliminer dans les petits espaces. Sa coordination pied-oeil lui permet d'être aussi "
        "efficace en dribble que dans le jeu sans ballon (appels de balle, deuxième poteau).",
        body_style))
    s.append(Paragraph(
        "Axes de progression : Jeu de tête (seulement 3 buts de la tête en carrière), régularité dans les grands "
        "matchs européens, leadership balle au pied sous pression. Luis Enrique travaille son placement défensif "
        "pour en faire un ailier complet.",
        body_style))

    s.append(Paragraph("Citations", h1_style))
    s.append(Paragraph(
        "<i>\"Bradley a la capacité de changer un match en une action. Sa progression est remarquable.\"</i> "
        "— Luis Enrique, entraîneur du PSG", body_style))
    s.append(Paragraph(
        "<i>\"Je veux gagner la Ligue des Champions avec Paris, c'est mon objectif numéro un.\"</i> "
        "— Bradley Barcola, mars 2026", body_style))

    s += sep()
    s.append(Paragraph("Fiche joueur FootPress AI • Donnees Opta/Transfermarkt • Mise a jour avril 2026", caption_style))
    build("profil_barcola_psg_2026.pdf", s)


# ─────────────────────────────────────────────
# PDF 5 — Ballon d'Or 2025 : bilan et favoris
# ─────────────────────────────────────────────
def pdf_ballon_or():
    s = []
    s.append(Paragraph("ANALYSE EDITORIALE", meta_style))
    s.append(Paragraph("Ballon d'Or 2025 — Bilan & Favoris 2026", title_style))
    s.append(Paragraph("Cérémonie 2025 | Theatre du Chatelet, Paris | Analyse FootPress AI", meta_style))
    s += sep()

    s.append(Paragraph("Ballon d'Or 2025 — Vainqueur", h1_style))
    s.append(Paragraph(
        "Vinicius Jr a remporté le Ballon d'Or 2025 lors d'une cérémonie historique au Theatre du Chatelet. "
        "L'ailier brésilien du Real Madrid a devancé Erling Haaland (Manchester City) et Lamine Yamal (FC Barcelone) "
        "au terme d'une saison 2024-2025 exceptionnelle : 28 buts, 18 passes décisives, vainqueur de la Ligue des Champions "
        "et du championnat d'Espagne. C'est son deuxième Ballon d'Or apres celui de 2023.",
        body_style))

    s.append(Paragraph("Top 10 du classement 2025", h1_style))
    palmares = [
        ["#", "Joueur",             "Club",              "Nationalite"],
        ["1", "Vinicius Jr",        "Real Madrid",       "Bresil"],
        ["2", "Erling Haaland",     "Manchester City",   "Norvege"],
        ["3", "Lamine Yamal",       "FC Barcelone",      "Espagne"],
        ["4", "Bukayo Saka",        "Arsenal FC",        "Angleterre"],
        ["5", "Jude Bellingham",    "Real Madrid",       "Angleterre"],
        ["6", "Florian Wirtz",      "Leverkusen",        "Allemagne"],
        ["7", "Bradley Barcola",    "PSG",               "France"],
        ["8", "Rodri",              "Manchester City",   "Espagne"],
        ["9", "Ruben Neves",        "Al-Hilal",          "Portugal"],
        ["10","Ousmane Dembele",    "PSG",               "France"],
    ]
    t = Table(palmares, colWidths=[0.8*cm, 5*cm, 4.5*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",   (0,1), (-1,1), "Helvetica-Bold"),
        ("BACKGROUND", (0,1), (-1,1), colors.HexColor("#fef9c3")),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,2), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",      (0,0), (0,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    s.append(t)
    s.append(Spacer(1, 0.4*cm))

    s.append(Paragraph("Favoris pour le Ballon d'Or 2026", h1_style))
    s.append(Paragraph(
        "A mi-saison 2025-2026, plusieurs prétendants se distinguent. Bukayo Saka (Arsenal) est en tête des pronostics "
        "grace a ses performances en Premier League et en Ligue des Champions. Bradley Barcola (PSG) est la surprise "
        "francaise avec 26 participations a des buts. Florian Wirtz (Leverkusen) maintient une regularite impressionnante.",
        body_style))

    s.append(Paragraph("<b>Cotes principales (bookmakers, avril 2026) :</b>", h2_style))
    cotes = [
        ["Joueur",            "Club",            "Cote"],
        ["Bukayo Saka",       "Arsenal",         "3.5"],
        ["Vinicius Jr",       "Real Madrid",     "4.0"],
        ["Lamine Yamal",      "FC Barcelone",    "5.0"],
        ["Bradley Barcola",   "PSG",             "6.0"],
        ["Florian Wirtz",     "Leverkusen",      "7.0"],
        ["Erling Haaland",    "Manchester City", "8.0"],
    ]
    t2 = Table(cotes, colWidths=[6*cm, 5*cm, 3*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GREEN),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",      (2,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    s.append(t2)

    s += sep()
    s.append(Paragraph("Analyse editoriale FootPress AI • Sources : France Football, UEFA, Opta • Avril 2026", caption_style))
    build("ballon_or_2025_analyse.pdf", s)


if __name__ == "__main__":
    print("Generation des PDFs FootPress AI...")
    pdf_psg_bayern()
    pdf_real_arsenal()
    pdf_ligue1_stats()
    pdf_profil_barcola()
    pdf_ballon_or()
    print(f"\nTous les fichiers sont dans : {OUTPUT_DIR}")
