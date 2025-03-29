// function showInput() {
//     document.getElementById('inputDiv').style.display = 'block';
// }

// function addAgent() {
//     var agentNumber = document.getElementById('agentInput').value;
    
//     var xhr = new XMLHttpRequest();
//     xhr.open("POST", "/add_agent", true);
//     xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    
//     xhr.onreadystatechange = function () {
//         if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
//             // Обновляем страницу после успешного добавления
//             location.reload();
//         }
//     };
    
//     // Отправляем введенное значение
//     xhr.send("agent_number=" + encodeURIComponent(agentNumber));
// }

// function StartTrade() {
//     document.getElementById('tradeWidget').style.display = 'block'; // Показываем виджет
// }

// function StartTrain() {
//     document.getElementById('trainWidget').style.display = 'block'; // Показываем виджет
// }

// function submitTrade() {
//     const URL = document.getElementById('url').value;
//     const agent = document.getElementById('agent').value;

//     // Здесь можно добавить логику для обработки данных
//     // console.log("Trade submitted:", { amount, currency });

//     // Дополнительно можно скрыть виджет после отправки
//     document.getElementById('tradeWidget').style.display = 'none';

//     alert('Trade submitted!');
// }

// function submitTrain() {
//     const URL = document.getElementById('url').value;

//     var xhr = new XMLHttpRequest();
//     xhr.open("POST", "/start_train", true);
//     xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    
//     xhr.onreadystatechange = function () {
//         if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
//             // Обновляем страницу после успешного добавления
//             location.reload();
//         }
//     };
    
//     // Отправляем введенное значение
//     xhr.send("URL=" + encodeURIComponent(URL));

//     document.getElementById('trainWidget').style.display = 'none';
// }