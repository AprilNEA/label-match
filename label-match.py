import asyncio
import argparse
from src import main
from loguru import logger

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--labelme_dir', type=str, default='', help='Location of the original labelme json datasets')
    parser.add_argument('--labelimg_dir', type=str, default='', help='Location of the original labelimg txt datasets')
    parser.add_argument('--output_dir', type=str, default='', help='Output location of the changed txt dataset')
    parser.add_argument('--classes_file', type=str, default='', help='Path to the file where the list of tags is saved')
    parser.add_argument('--logs_file', type=str, default='label-match_{time:YYYY-MM-DD_HH:mm:ss}',
                        help='Path to the file where log will be saved')
    args = parser.parse_args()
    # logger.remove(handler_id=None)
    # logger.add(sink=sys.stderr,
    #            level="DEBUG",
    #            colorize=True,
    #            format="{time} | {level} | {message}")

    logger.add(sink='label-match_{time}.log',
               level="DEBUG",
               colorize=True,
               format="{time:YYYY-MM-DD at HH:mm:ss} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}")
    try:
        asyncio.run(
            main.main(args.labelme_dir, args.labelimg_dir, args.output_dir, args.classes_file)
        )
    except OSError as e:
        print("Some thing wrong with OS system,maybe your path or file have something wrong.")
        print("Check your file and path.The programme will be exited.")
        exit()
    except RuntimeWarning as e:
        print("Some thing wrong with Coroutine system.")
        print("Please make a issue in Github with your ERROR code.")
        raise e
    finally:
        print("Finish")
