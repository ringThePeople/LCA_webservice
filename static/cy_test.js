$(function(){
    console.log('cy_test.js has been called')
    graph_data = $('#graph-info')[0].innerHTML.trim()
    var cy = window.cy = cytoscape({
        container: document.getElementById('cy'),
        wheelSensitivity: 0.1,
boxSelectionEnabled: false,
        avoidOverlap: true,
        avoidOverlapPadding: 10,
// autounselectify: true,
selectable: true,
// panningEnabled: false,
 userPanningEnabled: false,
zoomingEnabled: true,
        elements: [
        {
            group: 'node',
            // position: {
            //     x: 100,
            //     y: 100
            // },
            selectable: true
        }
        ],
        // layout: {
        //     name : 'dagre'    
        // },

        style: [
            {
                selector: 'node',
                style: {
                    'content': 'data(id)',
                    
                    'text-valign': 'center',
                    // 'text-halign': 'left',
                    'background-opacity': 0.5,
                    'width' : 52,
                    'height' : 52,
                    'border-width': 1,
                    'border-color': 'black'

                }
            },

            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'target-arrow-shape': 'triangle',
                    'line-color': '#7F7C7C',
                    'target-arrow-color': '#c0c0c0',
                    'curve-style': 'bezier'
                }
            },

            {
                selector: ':selected',
                style: {
        //             'background-color': 'black',
        //     'line-color': 'black',
        // 'target-arrow-color': 'black',
        // 'source-arrow-color': 'black',
        'opacity': 1
                }
            }

            

        ],

        elements: JSON.parse(graph_data)
    });

// download

// slect node color
for(var i=0;i<cy.$('node').length; i++){
    cy.$('node')[i].css("background-color", cy.$('node')[i].data('col'));
    cy.$('node')[i].css("x", cy.$('node')[i].data('x'));
    cy.$('node')[i].css("y", cy.$('node')[i].data('y'));
    cy.$('node')[i].renderedPosition("x", (cy.$('node')[i].data('x')));
    cy.$('node')[i].renderedPosition("y", (cy.$('node')[i].data('y')));

}
var jpg64 = cy.jpg();
// $("#jpg-eg").css("visibility", 'visible');
$('#jpg-eg').attr('href', jpg64);
// console.log('#jpg-eg');
// console.log(jpg64);

    
cy.on('select','node', function(event){
    console.log('node position');
    console.log(cy.$(':selected').position('x'));
    console.log(cy.$(':selected').position('y'));
     
});
cy.on('select','edge', function(event){
    console.log('edge select');
    console.log(cy.$(':selected').data());

    $("#cy-barP").html('In Period 1');

    if(typeof cy.$(':selected').data('dbsource') !== typeof undefined){
    $("#cy-barS").css("visibility", 'visible');
    $("#cy-barT").css("visibility", 'visible');
    $("#cy-barI").css("visibility", 'visible');
    $("#cy-barD").css("visibility", 'visible');

    
    str = "Source: " + cy.$(':selected').data('source');
    $("#cy-barS").html(str);
    
    str = "Target: " +  cy.$(':selected').data('target');
    $("#cy-barT").html(str);
    
    // str = "interaction: " + cy.$(':selected').data('interaction');
    // $("#cy-barI").html(str);
    
    str = "Edge Type: Inference + Prior Knowledge(" + cy.$(':selected').data('dbsource');
    str = str + ")"
    $("#cy-barD").html(str);
    }
    else{
    str = "Source: " + cy.$(':selected').data('source');
    $("#cy-barS").html(str);
    
    str = "Target: " +  cy.$(':selected').data('target');
    $("#cy-barT").html(str);

    str = "Edge Type: " + "Inference";
    $("#cy-barD").html(str);

     $("#cy-barI").css("visibility", 'hidden');   
     
    }

    });

    
    cy.panzoom({
    });
});

