esp32_ip = 'http://192.168.1.29/sinewave';  % Adjust to your ESP32's IP
json_file = 'sinewave.json';

h = plot(nan, nan, 'LineWidth', 2);
ylim([-1.2 1.2]);
xlabel("Sample Index");
ylabel("Amplitude");
title("Live Sinewave from ESP32");

while true
    try
        sinewave = webread(esp32_ip);  % ESP32 returns JSON array

        % Save to JSON file with timestamp
        data = struct('timestamp', datestr(now, 'yyyy-mm-dd HH:MM:SS'), ...
                      'sine', sinewave);
        jsonText = jsonencode(data);

        fid = fopen(json_file, 'w');
        fwrite(fid, jsonText, 'char');
        fclose(fid);

        % Update Plot
        set(h, 'YData', sinewave, 'XData', 1:length(sinewave));
        drawnow;
        pause(1);

    catch ME
        warning("⚠️ Error: %s", ME.message);
        pause(2);
    end
end
