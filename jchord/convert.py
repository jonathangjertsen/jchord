from argparse import ArgumentParser
import sys

import jchord


def is_txt(f):
    return f.endswith(".txt")


def is_xlsx(f):
    return f.endswith((".xls", ".xlsx"))


def is_pdf(f):
    return f.endswith(".pdf")


def is_midi(f):
    return f.endswith((".mid", ".midi"))


def parse_arglist(arglist):
    if not arglist:
        return {}
    try:
        return dict(arg.split("=") for arg in arglist.split(","))
    except:
        print(
            f"Couldn't parse arglist, expected key1=value,key2=value..., got {arglist}"
        )
        return None


def main():
    parser = ArgumentParser(
        description="Converts between different representations of the same format\n"
    )
    parser.add_argument(
        "file_in", help="Input progression as string, .txt, .xlsx or .midi"
    )
    parser.add_argument("file_out", help="Output file as .txt, .xlsx, .midi or .pdf")
    parser.add_argument(
        "--midi",
        help="comma separated list of arguments for midi, e.g. tempo=8,beats_per_chord=2",
    )
    parser.add_argument(
        "--pdf",
        help="comma separated list of arguments for pdf, e.g. chords_per_row=8,fontsize=30",
    )
    args = parser.parse_args()
    file_in = args.file_in
    file_out = args.file_out

    if is_txt(file_in):
        progression = jchord.ChordProgression.from_txt(file_in)
    elif is_xlsx(file_in):
        progression = jchord.ChordProgression.from_xlsx(file_in)
    elif is_midi(file_in):
        progression = jchord.ChordProgression.from_midi(file_in)
    elif is_pdf(file_in):
        print("Sorry, converting from PDF is not supported")
        return -1
    else:
        progression = jchord.ChordProgression.from_string(file_in)

    if is_txt(file_out):
        progression.to_txt(file_out)
    elif is_xlsx(file_out):
        progression.to_xlsx(file_out)
    elif is_midi(file_out):
        midi_args = parse_arglist(args.midi)
        if midi_args is None:
            return -2
        progression.to_midi(
            jchord.MidiConversionSettings(filename=file_out, **midi_args)
        )
    elif is_pdf(file_out):
        pdf_args = parse_arglist(args.pdf)
        if pdf_args is None:
            return -2
        progression.to_pdf(file_out, **pdf_args)
    else:
        print(f"Unknown format: {file_out}")
        return -2
    return 0


if __name__ == "__main__":
    sys.exit(main())
