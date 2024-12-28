#include <stdio.h>
#include <stdint.h>

#define DURATION_MULTIPLIER 1000000

typedef struct {
    char riff[4];        // "RIFF"
    uint32_t size;       // Size of the entire file in bytes minus 8 bytes for the two fields not included in this count: 'RIFF' and size.
    char wave[4];        // "WAVE"
    char fmt[4];         // "fmt "
    uint32_t fmt_size;   // Size of the fmt chunk
    uint16_t format;     // Audio format, 1 for PCM
    uint16_t channels;   // Number of channels
    uint32_t sample_rate;// Sampling rate
    uint32_t byte_rate;  // (Sample Rate * BitsPerSample * Channels) / 8
    uint16_t block_align;// (BitsPerSample * Channels) / 8
    uint16_t bits_per_sample; // Bits per sample
    char data[4];        // "data"
    uint32_t data_size;  // Size of the data section
} wav_header;

__declspec(dllexport) double aci(const char *file) {
    printf("received file: %s\n", file);
    FILE *fp = fopen(file, "rb");

    if (fp == NULL) {
        perror("Error opening file");
        return -1;
    }

    wav_header header;
    if (fread(&header, sizeof(wav_header), 1, fp) != 1) {
        printf("Error: failed to read header\n");
        fclose(fp);
        return -1;
    }

    // Print some information about the file headers
    printf("%s info:\n", file);


    // Calculate duration
    double duration = (double)header.data_size / (header.sample_rate * header.channels * (header.bits_per_sample / 8.0)) * DURATION_MULTIPLIER;
    printf("Duration: %f Seconds\n", duration);

    fclose(fp);
    return duration;
}