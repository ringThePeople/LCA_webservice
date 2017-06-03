$(function(){
    console.log('cy_test5.js has been called')
    graph_data = $('#graph-info5')[0].innerHTML.trim()
    var cy = window.cy = cytoscape({
        container: document.getElementById('cy5'),
        wheelSensitivity: 0.1,
boxSelectionEnabled: false,
// autounselectify: true,
selectable: true,
        elements: [
        {
            group: 'node',
            
            selectable: true
        }
        ],
        
        style: [
            {
                selector: 'node',
                style: {
                    'content': 'data(id)',
                    
                    'text-valign': 'center',
                    
                    'background-opacity': 0.5,
                    'width' : 75,
                    'height' : 75,
                    'border-width': 1,
                    'border-color': 'black'
                }
            },

            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'target-arrow-shape': 'triangle',
                    'line-color': '#c0c0c0',
                    'target-arrow-color': '#c0c0c0',
                    'curve-style': 'bezier'
                }
            },

            {
                selector: ':selected',
                style: {
                    
        'opacity': 1
                }
            }

            

        ],

        elements: JSON.parse(graph_data)
    });


// slect node color
for(var i=0;i<cy.$('node').length; i++){
    cy.$('node')[i].css("background-color", cy.$('node')[i].data('col'));
    cy.$('node')[i].renderedPosition("x", (cy.$('node')[i].data('x')*40 + 30));
    cy.$('node')[i].renderedPosition("y", (cy.$('node')[i].data('y')*20 - 50));
}

// download
var jpg64 = cy.jpg();
$('#jpg-eg5').attr('href', jpg64);

cy.on('select','edge', function(event){

    console.log('select');
    console.log(cy.$(':selected').data());

    $("#cy-barP").html('In Period 5');

    if(typeof cy.$(':selected').data('dbsource') !== typeof undefined){
    $("#cy-barS").css("visibility", 'visible');
    $("#cy-barT").css("visibility", 'visible');
    $("#cy-barI").css("visibility", 'visible');
    $("#cy-barD").css("visibility", 'visible');
    
    str = "source: " + cy.$(':selected').data('source');
    $("#cy-barS").html(str);
    
    str = "target: " +  cy.$(':selected').data('target');
    $("#cy-barT").html(str);
    
    str = "interaction: " + cy.$(':selected').data('interaction');
    $("#cy-barI").html(str);
    
    str = "dbsource: " + cy.$(':selected').data('dbsource');
    $("#cy-barD").html(str);
    }
    else{
    str = "source: " + cy.$(':selected').data('source');
    $("#cy-barS").html(str);
    
    str = "target: " +  cy.$(':selected').data('target');
    $("#cy-barT").html(str);

    str = "dbsource: " + "link_source";
    $("#cy-barD").html(str);

     $("#cy-barI").css("visibility", 'hidden');   
     
    }

    });



});

