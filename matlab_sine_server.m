esp32_ip = 'http://192.168.1.29/sine';  % Replace with your ESP32 IP
json_file = 'sinewave.json';

while true
    try
        response = webread(esp32_ip);  % Get sinewave string
        sinewave = str2double(split(response, ','));  % Convert to array

        % Save to JSON file
        data = struct('timestamp', datestr(now, 'yyyy-mm-dd HH:MM:SS'), 'sine', sinewave);
        jsonText = jsonencode(data);

        fid = fopen(json_file, 'w');
        fwrite(fid, jsonText, 'char');
        fclose(fid);

        % Optional plot
        plot(sinewave);
        ylim([-1.2 1.2]);
        title("Live Sinewave from ESP32");
        drawnow;

    catch ME
        warning("⚠️ Error: %s", ME.message);
    end
    pause(1);
end
