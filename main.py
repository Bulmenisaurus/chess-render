import glob
import os
from PIL import Image, ImageDraw


# parses chess notation into a sequence of moves, specifically Args[][], or str[][][]
def parse_specialized_chess_notation(moves: str) -> list:
    return [[args.strip().split(" ") for args in line.split(";")] for line in moves.strip().split("\n")]


def init_board() -> list:
    return list('rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR')


# converts a string like "e5" to the corresponding index on the board
def parse_board_pos(position: str) -> int:
    x_name = position[0].lower()
    y_name = position[1]

    x = 'abcdefgh'.index(x_name)
    y = 8 - int(y_name)

    return x + 8 * y


def apply_move(b: list, move: list) -> list:
    board = b.copy()
    if move[0] == "m":
        idx_from = parse_board_pos(move[1])
        idx_to = parse_board_pos(move[2])

        board[idx_to] = board[idx_from]
        board[idx_from] = '.'
    else:
        raise ValueError(f"Unknown move type `{move[0]}` in {move}")

    return board


# https://pillow.readthedocs.io/en/stable/
def write_board_image(board: list, file_name: str, directory: str, highlight_squares: list, highlight_pieces: list):
    image = Image.new("RGBA", (720, 720), "black")

    chess_render_colors = {
        "black": "rgb(179, 135, 101)",
        "white": "rgb(238, 216, 182)"
    }

    # white uppercase, black lowercase
    pieces_images = {
        "r": Image.open("./sprites/Chess_rdt60.png"),
        "R": Image.open("./sprites/Chess_rlt60.png"),
        "q": Image.open("./sprites/Chess_qdt60.png"),
        "Q": Image.open("./sprites/Chess_qlt60.png"),
        "p": Image.open("./sprites/Chess_pdt60.png"),
        "P": Image.open("./sprites/Chess_plt60.png"),
        "n": Image.open("./sprites/Chess_ndt60.png"),
        "N": Image.open("./sprites/Chess_nlt60.png"),
        "k": Image.open("./sprites/Chess_kdt60.png"),
        "K": Image.open("./sprites/Chess_klt60.png"),
        "b": Image.open("./sprites/Chess_bdt60.png"),
        "B": Image.open("./sprites/Chess_blt60.png")
    }

    # resize each image to 80x80
    for key in pieces_images:
        pieces_images[key] = pieces_images[key].resize((90, 90))

    # 1. Draw the tiles
    tile_size = int(image.width / 8)
    draw = ImageDraw.Draw(image)
    for x in range(8):
        for y in range(8):
            piece_chess_color = ["white", "black"][(x + y) % 2]
            draw.rectangle(
                (x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size),
                fill=chess_render_colors[piece_chess_color]
            )

    # 2. Draw the pieces
    for x in range(8):
        for y in range(8):
            idx = x + 8 * y
            piece = board[idx]
            if piece == ".":
                continue
            piece_image = pieces_images[piece]
            # https://pillow.readthedocs.io/en/stable/reference/Image.html?highlight=paste#PIL.Image.Image.paste

            image.paste(piece_image, (x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size),
                        piece_image)

    image.save(f'{directory}image_{file_name}.png')


def chess_boards_from_moves(move_str: str, dir_path: str):
    moves = parse_specialized_chess_notation(move_str)

    board = init_board()

    write_board_image(board, '0', dir_path, [], [])

    for (i, moves_in_turn) in enumerate(moves):
        for move in moves_in_turn:
            board = apply_move(board, move)
        write_board_image(board, str(i + 1), dir_path, [], [])
        print(f"{i}/{len(moves)}")


# https://imageio.readthedocs.io/en/stable/examples.html#optimizing-a-gif-using-pygifsicle
def gif_from_dir(input_directory: str, output_filename: str):
    gif_frames = []

    # https://docs.python.org/3/library/glob.html
    image_filenames = glob.glob(input_directory + "*")

    for filename in sorted(image_filenames):
        # glob.glob returns filenames relative to the input dir, so no need to concatenate the filename with the
        # directory name here
        gif_frames.append(Image.open(filename))

    # TODO: compress
    print(gif_frames)
    first_frame = gif_frames.pop(0)
    first_frame.save(f"{output_filename}", format="GIF", append_images=gif_frames, save_all=True, duration=500, loop=0)


# there are so many packages available for this kind of stuff,
# os, shutil, glob, pathlib
def clear_dir(directory: str):
    for file in glob.glob(directory + "*"):
        os.remove(file)


def main():
    #     R g2 h1 2
    moves = """
m d1 h1
m e2 e3
m e3 d3
m d3 d4; m d4 c4"""
    # https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
    chess_boards_from_moves(moves, "./images/")
    gif_from_dir("./images/", "./output/output.gif")
    clear_dir("./images/")


if __name__ == '__main__':
    main()
