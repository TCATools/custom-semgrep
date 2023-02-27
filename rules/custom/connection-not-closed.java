package rules.custom.main;

public void toConnection() {
    Connection conn = null;
    try {
        DataSource datasource = (DataSource) SpringBeanUtil.getBean("data");
        // ruleid: connection-not-closed
        conn = datasource.getConnection();

        // JdbcUtils.closeConnection(conn);
    }
    catch (Exception e) {
        System.out.println(e);
    } finally {
        // conn.close();
        // JdbcUtils.closeConnection(conn);
    }
}
