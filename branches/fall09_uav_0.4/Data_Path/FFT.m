fd = fopen('fft_data', 'r')
temp = fread(fd);
spec = fft2(temp, 1024)
plot(linspace(-256e3/2, 256e3/2, 1024), abs(spec))
