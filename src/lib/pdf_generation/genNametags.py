import labels, os
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.lib import colors
from lib.utils.pdf import add_text_field, NAMETAG_FONT_PATH
from lib.utils.WCA_result_to_string import format_result

# FEMALE_POLICE_OFFICER = '\u1F46E\u200D\u2640\uFE0F'
# MALE_POLICE_OFFICER = '\u1F46E'
# FEMALE_CONSTRUCTION_WORKER = '\u1F477\u200D\u2640\uFE0F'
# MALE_CONSTRUCTION_WORKER = '\u1F477'
FOOTER_HEIGHT = 7
FOOTER_SIDE_MARGIN = 10

def gen_nametags(competition_name, persons):
    ### Initialize font
    registerFont(TTFont('Trebuchet', NAMETAG_FONT_PATH))

    # Format information for nametags: DIN-A4 layout with 2 rows of 4 nametags each with a size of 85x55mm
    specs = labels.Specification(210, 297, 2, 4, 85, 55)

    # Local function for nametag layout. Heavily uses add_text_field and is passed to sheet creation
    # obj is one list element of persons, i.e. one dict from utils/data_from_WCIF.get_nametag_data()
    def create_nametag(label, width, height, obj):
        competition_name = obj[0]
        person = obj[1]

        # Write competition name, competitor name and nation
        add_text_field(label, competition_name, width / 2.0, height - 25, max_width=width-5, max_font_size=50, font="Helvetica")
        
        name = person['name']
        # Add delegate / organizer color
        if person['delegate']:
            name_color = colors.red
            name = name + " (Delegate)" # Eventually replace with
        elif person['organizer']:
            name_color = colors.red
            name = name + " (Orga)"     # emoji support (see constants at top of file)
        else:
            name_color = colors.black

        add_text_field(label, name, width/2.0, height/2.0, max_width=width-5, max_font_size=25, color=name_color)

        add_text_field(label, person['nation'], width/2.0, height/3.0, max_width=150, max_font_size=20, color=colors.black)

        if person['wcaId'] == None:
            # Add newcomer label
            add_text_field(label, "Newcomer!", width/2.0, FOOTER_HEIGHT, font_size=30, color=colors.green)
        else:
            # Add 3x3 PBs, comp_count and Best
            if person['_3x3']['single'] != -1 and person['_3x3']['average'] != -1:
                rubiks_text = "3x3 PBs: {} S / {} A".format(format_result(person['_3x3']['single']), format_result(person['_3x3']['average']))
                if (person['best']['eventName'] != '3x3x3'):
                    add_text_field(label, rubiks_text, FOOTER_SIDE_MARGIN, FOOTER_HEIGHT + 10, font_size=10, color=colors.blue, position="start")

            best_text = "Best World Ranking: {} ({} {} of {})".format(
                person['best']['ranking'],
                person['best']['eventName'],
                person['best']['type'],
                format_result(person['best']['result'], person['best']['eventName'])
            )
            add_text_field(label, best_text, FOOTER_SIDE_MARGIN, FOOTER_HEIGHT, max_width=width-20, max_font_size=10, color=colors.blue, position="start")

            comp_count = "Competition # " + str(person['numComps'] + 1)
            add_text_field(label, comp_count, width - FOOTER_SIDE_MARGIN, FOOTER_HEIGHT + 10, font_size=10, color=colors.blue, position="end")

    # Create the sheet and add labels
    sheet = labels.Sheet(specs, create_nametag, border=True)
    sheet.add_labels((competition_name, person) for person in persons)

    # Check if folder is there or create, and safe in folder
    competition_name_stripped = competition_name.replace(" ", "")
    if not os.path.exists(competition_name_stripped):
        os.makedirs(competition_name_stripped)
    
    nametag_file = competition_name_stripped + '/Nametags.pdf'
    sheet.save(nametag_file)
    print("{0:d} nametags output on {1:d} pages.".format(sheet.label_count, sheet.page_count))
