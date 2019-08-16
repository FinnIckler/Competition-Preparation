import labels, os, sys
from reportlab.graphics import shapes
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.lib import colors

#FEMALE_POLICE_OFFICER = '\u1F46E\u200D\u2640\uFE0F'
#MALE_POLICE_OFFICER = '\u1F46E'
#FEMALE_CONSTRUCTION_WORKER = '\u1F477\u200D\u2640\uFE0F'
#MALE_CONSTRUCTION_WORKER = '\u1F477'
FOOTER_HEIGHT = 7

def shrink_or_enlarge_string(input_string, add_string, string_length):
    while len(input_string) > string_length:
        input_string = input_string[1:]
    while len(input_string) < string_length:
        input_string = add_string + input_string
    return input_string

# Input: event this is about, time (per default in ms, different depending on event)
# Output: String of format s.mm, ss.mm, min:ss.mm accordingly
def format_result(result, event='3x3x3'):
    if event == '3x3x3 Fewest Moves':
        return format_result_FMC(result)

    elif event == '3x3x3 Multi-Blindfolded':
        return format_result_multi(result)

    elif result > 10 * 60 * 100: # mins * secs * millisecs
        return format_result_OVER_10MIN(result)

    elif result < 60 * 100: # mins * millisecs
        return format_result_UNDER_1MIN(result)

    else:
        minutes = int(result / 6000)
        return shrink_or_enlarge_string(str(minutes), '0', 2) + ":" + format_result_UNDER_1MIN(result % 6000)

def format_result_multi(result):
    missed = result % 100
    time_in_sec = int((result % 1000000) / 100)
    minutes, seconds = int(time_in_sec / 60), time_in_sec % 60
    difference = 99 - int(result / 10000000)
    solved = difference + missed
    attempted = solved + missed

    return str(solved) + "/" + str(attempted) + " in " + str(minutes) + ":" + str(seconds)

def format_result_FMC(result):
    # Single
    if result < 100:
        return str(result)
    # Mean of 3
    else:
        moves, millimoves = int(result / 100), result % 100
        return str(moves) + "." + str(millimoves)

def format_result_OVER_10MIN(result):
    minutes, seconds = int(result / 6000), result % 6000
    return shrink_or_enlarge_string(str(minutes), '0', 2) + ":" + shrink_or_enlarge_string(str(seconds), '0', 2) + "." + str(result % 100)

def format_result_UNDER_1MIN(result):
    seconds, millis = int(result / 100), result % 100
    return str(seconds) + "." + shrink_or_enlarge_string(str(millis), '0', 2)

# Add String text to label at (width, height). Font_size gets adjusted to max_width
# You can add a max_font_size where the calculation starts
def add_text_field(label, text, width, height, max_width=-1, max_font_size=100, font_size=-1, font = "Arial", color=colors.black, position="middle"):
    if max_width == -1:
        max_width = width

    if font_size == -1:
        while stringWidth(text, font, max_font_size) > max_width:
            max_font_size *= 0.9
        font_size = max_font_size

    s = shapes.String(width, height, text, textAnchor=position)
    s.fontName = font
    s.fontSize = font_size
    s.fillColor = color
    label.add(s)

def gen_nametags(competition_name, persons):
    ### Initialize font
    if not os.path.isfile('data/Trebuchet.ttf'):
        print("ERROR!! File 'Trebuchet.ttf' does not exist. Please download from \n",
            "https://www.fontpalace.com/font-download/Trebuchet+MS/\n and add to",
            "{}/.".format(os.path.dirname(os.path.abspath(__file__))))
        sys.exit()

    registerFont(TTFont('Arial', 'Trebuchet.ttf'))

    # dirname = os.path.dirname(".")
    # wca_logo = file1 = os.path.join(dirname, "wca.png")
    # Format information for nametags: usual DIN-A4 layout with 2 rows of 4 nametags each with a size of 85x55mm
    specs = labels.Specification(210, 297, 2, 4, 85, 55)

    def create_nametag(label, width, height, obj):
        competition_name = obj[0]
        person = obj[1]

        # Write the title.
        add_text_field( label,
                        competition_name,
                        width/2.0,
                        height-20,
                        max_width = width - 5,
                        font="Arial")

        # Add the name
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

        # Measure the width of the name and shrink the font size until it fits.
        add_text_field( label,
                        name,
                        width/2.0,
                        height/2.0,
                        max_width=width-5,
                        font="Arial",
                        max_font_size=30,
                        color=name_color)

        # Add the nation
        add_text_field( label,
                        person['nation'],
                        width/2.0,
                        height/3.0,
                        max_width=80,
                        font="Arial",
                        max_font_size=20,
                        color=colors.black)

        if person['wcaId'] == 'null':
            # Add newcomer label
            add_text_field(label, "Newcomer!", width/2.0, FOOTER_HEIGHT, font="Arial", font_size=30, color=colors.green)
        else:
            rubiks_text = "3x3 PBs: {} S / {} A".format(format_result(person['_3x3']['single']), format_result(person['_3x3']['average']))

            best_text = "Best World Ranking: {} ({} {} of {})".format(
                person['best']['ranking'],
                person['best']['eventName'],
                person['best']['type'],
                format_result(person['best']['result'], person['best']['eventName'])
            )

            # Add 3x3 PBs, comp_count and Best
            if (person['best']['eventName'] != '3x3x3'):
                add_text_field( label,
                                rubiks_text,
                                10,
                                FOOTER_HEIGHT + 10,
                                font="Arial",
                                font_size=10,
                                color=colors.blue,
                                position="start")

            add_text_field( label,
                            "Competition # " + str(person['numComps'] + 1),
                            width - 10,
                            FOOTER_HEIGHT + 10,
                            font="Arial",
                            font_size=10,
                            color=colors.blue,
                            position="end")

            add_text_field( label,
                            best_text,
                            10,
                            FOOTER_HEIGHT,
                            font="Arial",
                            max_width=width-20,
                            max_font_size=10,
                            color=colors.blue,
                            position="start")

    # Create the sheet.
    sheet = labels.Sheet(specs, create_nametag, border=True)

    # Add every person individually to the labels
    sheet.add_labels((competition_name, person) for person in persons)



    # Check if folder is there or create, and safe in folder
    # TODO

    # Save the file and we are done.
    nametag_file = 'Nametags.pdf'
    sheet.save(nametag_file)
    print("{0:d} label(s) output on {1:d} page(s).".format(sheet.label_count, sheet.page_count))
