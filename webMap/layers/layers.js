var wms_layers = [];


        var lyr_StamenTonerLight_0 = new ol.layer.Tile({
            'title': 'Stamen Toner Light',
            'type': 'base',
            'opacity': 1.000000,
            
            
            source: new ol.source.XYZ({
    attributions: ' ',
                url: 'http://tile.stamen.com/toner-lite/{z}/{x}/{y}.png'
            })
        });
var format_mappa_finale_1 = new ol.format.GeoJSON();
var features_mappa_finale_1 = format_mappa_finale_1.readFeatures(json_mappa_finale_1, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_mappa_finale_1 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_mappa_finale_1.addFeatures(features_mappa_finale_1);
var lyr_mappa_finale_1 = new ol.layer.Vector({
                declutter: true,
                source:jsonSource_mappa_finale_1, 
                style: style_mappa_finale_1,
                interactive: true,
                title: 'mappa_finale'
            });

lyr_StamenTonerLight_0.setVisible(true);lyr_mappa_finale_1.setVisible(true);
var layersList = [lyr_StamenTonerLight_0,lyr_mappa_finale_1];
lyr_mappa_finale_1.set('fieldAliases', {'id': 'id', 'ID_E': 'ID_E', 'highway': 'highway', 'bicycle': 'bicycle', 'foot': 'foot', 'lanes': 'lanes', 'cycleway': 'cycleway', 'segregated': 'segregated', 'maxspeed': 'maxspeed', 'route': 'route', 'D_TY_PZ_CC': 'D_TY_PZ_CC', 'class_1': 'class_1', 'class_2': 'class_2', 'classifica': 'classifica', });
lyr_mappa_finale_1.set('fieldImages', {'id': '', 'ID_E': '', 'highway': '', 'bicycle': '', 'foot': '', 'lanes': '', 'cycleway': '', 'segregated': '', 'maxspeed': '', 'route': '', 'D_TY_PZ_CC': '', 'class_1': '', 'class_2': '', 'classifica': '', });
lyr_mappa_finale_1.set('fieldLabels', {'id': 'no label', 'ID_E': 'no label', 'highway': 'no label', 'bicycle': 'no label', 'foot': 'no label', 'lanes': 'no label', 'cycleway': 'no label', 'segregated': 'no label', 'maxspeed': 'no label', 'route': 'no label', 'D_TY_PZ_CC': 'no label', 'class_1': 'no label', 'class_2': 'no label', 'classifica': 'no label', });
lyr_mappa_finale_1.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});