#include <stdio.h>
#include <libavformat/avformat.h>
#include <libavutil/timestamp.h>
#include <libavutil/dict.h>
#include <libavutil/time.h>

__declspec(dllexport) double aci(char* file) {
    AVFormatContext *formatContext = NULL;
    int ret;
    if ((ret = avformat_open_input(&formatContext, file, NULL, NULL )) < 0) {
        fprintf(stderr, "File could not open: %s\n", file);
        return -1;
    }
    if ((ret = avformat_find_stream_info(formatContext, NULL)) < 0) {
        fprintf(stderr, "Could not find stream info.\n");
        return -1;
    }
    int64_t duration = formatContext->duration;
    printf("duration: %.2f seconds\n", (double)duration / AV_TIME_BASE);
    avformat_close_input(&formatContext);
    return 0;
}