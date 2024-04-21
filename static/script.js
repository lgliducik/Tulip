function myFunction(taskId)
  {
  console.log(taskId)
      axios.post('/update_task', {
      params: {
        "task_id": taskId
    }
  })

}
