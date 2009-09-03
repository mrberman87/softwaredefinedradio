function UAV_fft2

  data = read_complex_binary("~/softwaredefinedradio/src/FFT/RC.dat", 1024);
  #kp = fopen("~/Desktop/data.txt", "wb");
  #kp_1 = fwrite(kp, data, "float");
  #fclose(kp);
  plotfft(data,256e3)
  print("~/Desktop/FFT_image.jpeg")

endfunction

function v = read_complex_binary (filename, count)

  m = nargchk (1,2,nargin);
  if (m)
    usage (m);
  end

  if (nargin < 2)
    count = Inf;
  end

  f = fopen (filename, 'rb');
  if (f < 0)
    v = 0;
  else
    t = fread (f, [2, count], 'float');
    fclose (f);
    v = t(1,:) + t(2,:)*i;
    [r, c] = size (v);
    v = reshape (v, c, r);
  end
endfunction

function plotfft (data, sample_rate)

  if (nargin == 1)
    sample_rate = 1.0;
  endif;

  if ((m = nargchk (1,2,nargin)))
    usage (m);
  endif;

  len = length(data);
  #s = fft (data*kaiser(len, 5));
  s = fft(data);

  incr = sample_rate/len;
  min_x = -sample_rate/2;
  max_x = sample_rate/2 - incr;
  plot (min_x:incr:max_x, 20*log10(abs(fftshift(s))));

endfunction

