function Plot_Bscan_HDF5(filename, want_to_save, output_path)
    % Bscan - Genera un B-scan a partir de los datos en un archivo HDF5

    % Entradas:
    %   * filename - Nombre del archivo HDF5 que contiene los datos de
    %   amplitud y tiempo. Son los archivos .out de gprMax
    %   * opcional: want_to_save - Por defecto False. 
    %       Si False, muestra el B-scan en pantalla y no se guarda.
    %       Si True, no se muestra el B-scan en pantalla y se guarda el B-scan en output_path,
    %   * opcional: output_path - Ruta en la que se guardará en el
    %   Plot_Bscan_HDF5 si want_to_save =  True 

    % Salida:
    %   Grafico B-scan de la amplitud en función de la posición y el
    %   tiempo. Se guarda en output_path. 
    
    % Valores predeterminados para argumentos opcionales
    if nargin < 2
        want_to_save = false; % Por defecto no guardar
    end
    if nargin < 3 || isempty(output_path)
        output_path = pwd; % Usar la carpeta actual por defecto
    end

    % Datos
    rx_path = '/rxs/rx1/Ey';
    A = h5read(filename, rx_path)'; %amplitudes
    iterations = size(A,1);
    nAscans = size(A,2);

    % Posición
    x = (0:nAscans-1);

    % Tiempo
    dt = h5readatt(filename, '/', 'dt'); % Escala del tiempo
    t = (0:iterations-1) * dt;

    % Matrices únicas para posición y tiempo
    xu = unique(x)';
    tu = unique(t)';
    Aq = reshape(A, [size(tu,1), size(xu,1)]);

    % Gráfico B-scan
    fig = figure('Visible', 'off'); % Ocultar figura inicialmente
    imagesc(xu, tu, Aq);
    colormap('gray');
    colorbar;
    xlabel('Número de A-scans (posición)');
    ylabel('Tiempo (s)');
    title('B-scan');

    % Guardar o mostrar
    if want_to_save
        save_path = fullfile(output_path, 'Bscan.png');
        saveas(fig, save_path);
        close(fig); % Cerrar figura después de guardar
        disp(['B-scan guardado en: ', save_path]);
    else
        % Mostrar figura en pantalla
        set(fig, 'Visible', 'on');
    end
end
