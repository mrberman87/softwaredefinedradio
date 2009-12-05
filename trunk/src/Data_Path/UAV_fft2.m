function UAV_fft2 (real_path, imag_path, to_path)
  
  real_data = read_float_binary(real_path, 4096);
  imaginary_data = read_float_binary(imag_path, 4096);
  data = combine_real_imaginary(real_data, imaginary_data);
  plot(linspace(-256e3/2, 256e3/2, 1024), 20*log10(abs(fftshift((1/1024)*fft(data)))));
  print(to_path)
  quit()
  
endfunction

function v = read_float_binary (filename, count)

  %% usage: read_float_binary (filename, [count])
  %%  open filename and return the contents, treating them as
  %%  32 bit floats

  f = fopen (filename, 'rb');
  if (f < 0)
    v = 0;
  else
    v = fread (f, count, 'float');
    fclose (f);
  end
endfunction

function data = combine_real_imaginary(real_data, imaginary_data)
  data = zeros(1,1024);
  for i = 1:1024
	data(i) = real_data(i+2048) + imaginary_data(i+2048)*j;
  end
endfunction
