/**
 * Home page - migrated from top.jsp
 */
import FlightSearchForm from '../components/common/FlightSearchForm';

export default function Home() {
  return (
    <div className="row">
      <section className="col-md-4">
        <h2>空席照会・ご予約</h2>
        <FlightSearchForm />
      </section>

      <section className="col-md-8">
        <h2 id="description-heading">ATRSについて</h2>

        <section>
          <h3>概要</h3>
          <p>
            ATRS（本アプリケーション）は、Macchinetta オンライン版 フレームワーク、Macchinetta クライアント基本版
            フレームワーク（以下、フレームワーク）を用いたサンプルアプリケーションです。
          </p>
          <dl>
            <dt>バージョン</dt>
            <dd>1.11.0.RELEASE (React SPA)</dd>
          </dl>
        </section>

        <section>
          <h3>ATRSの利用方法</h3>
          <ul>
            <li>
              ATRSにログインする場合は、ログインボタンを押して、会員番号とパスワードを入力してログインしてください。
            </li>
            <li>
              ATRSからログアウトする場合は、ログインユーザメニューからログアウトを選択してください。
            </li>
            <li>
              フライトの空席状況を照会する場合は、国内線リンクを選択して空席照会へ進むか、
              本画面よりフライト種別、区間、搭乗日、搭乗クラスを選択の上、照会ボタンを押してください。
            </li>
            <li>
              続けてチケットを予約する場合は、フライトの選択、お客様情報を入力した上で、
              予約内容の確認を行い、予約の確定を実施してください。
            </li>
            <li>ATRSカード会員に入会する場合は、会員登録を押してください。</li>
            <li>
              ATRSカード会員情報を変更する場合は、ログインした後、ログインユーザメニューから会員情報変更を選択してください。
            </li>
          </ul>
        </section>

        <section>
          <h3>ATRSで使用しているフレームワークの機能</h3>
          <p>
            ATRSで使用しているフレームワークの機能については、サンプルアプリケーションマニュアルを参照してください。
          </p>
        </section>
      </section>
    </div>
  );
}
