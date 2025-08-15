<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const clientes = ref([]);

onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/clientes/');
    clientes.value = response.data.results;
    console.log("Clientes carregados:", clientes.value);
  } catch (error) {
    console.error("Houve um erro ao buscar os clientes:", error);
  }
});
</script>

<template>
  <header>
    <h1>Mister Ottani Vendas PRO</h1>
  </header>

  <main>
    <h2>Lista de Clientes (Vindos da API Django)</h2>
    <div v-if="clientes.length > 0">
      <ul>
        <li v-for="cliente in clientes" :key="cliente.id">
          {{ cliente.razao_social }} - Score: {{ cliente.score_potencial }}
        </li>
      </ul>
    </div>
    <div v-else>
      <p>Carregando clientes ou nenhum cliente encontrado...</p>
    </div>
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
  background-color: #333;
  color: white;
  padding: 1rem 2rem;
}
main {
  padding: 2rem;
}
</style>